from io import BytesIO
from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.core.files.images import ImageFile
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.forms.utils import ErrorList
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, render_to_response
from django.utils.decorators import method_decorator
from django.utils.http import is_safe_url
from django.views.decorators.csrf import csrf_protect
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView
from django.views.generic.list import ListView
from buzzit_app.forms import RegistrationForm
from buzzit_models.models import *
from django.contrib.auth.forms import AuthenticationForm
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib.auth import login, logout as authlogout
from django.contrib.auth.views import password_change as _pw_change_
import logging
from django.forms.fields import FileField, ClearableFileInput
from django.core.exceptions import ObjectDoesNotExist
from PIL import Image
import imghdr
import os
from django.contrib import messages
from django.core.mail import send_mail


def start(request):
    """
    Controls the behaviour of guests visiting the page and the login procedure.
    If a user is already authenticated he gets redirected to his home.
    Else a login form is provided.

    :param request: The request object
    :return: start.html template rendered with a login form element "form"
    """
    if request.user.is_authenticated():
        if not request.user.is_active:
            messages.error(request, "Sie sind deaktiviert!")
            return render(request, "guest/start.html", {"form": AuthenticationForm()})
        return HttpResponseRedirect(reverse("home"))
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user:
                if not user.is_active:
                    messages.error(request, "Sie sind deaktiviert!")
                    return render(request, "guest/start.html", {"form": AuthenticationForm()})
                login(request, user)
                messages.success(request, "Sie wurden eingeloggt!")
                redirect_to = request.REQUEST.get("next", False)
                if (redirect_to):
                    if not is_safe_url(url=redirect_to, host=request.get_host()):
                        return HttpResponseRedirect(reverse("home"))
                    return HttpResponseRedirect(redirect_to)
                return HttpResponseRedirect(reverse("home"))
        else:
            messages.error(request, "Benutzername/Passwort falsch!")
    else:
        form = AuthenticationForm()
    return render(request, "guest/start.html", {"form": form})


@login_required
def home(request):
    """
    The start page of logged in users.
    :param request: The request object.
    :return: the home.html template rendered with a user object "user" and a profile object "profile"
    """
    circles_of_which_we_are_member = Circle.objects.filter(members=request.user.pk)
    message_list = []
    # nachrichten von usern denen, wir folgen, und in deren kreis wir sind:
    for circle in circles_of_which_we_are_member:
        message_list += (circle.messages.all())
    # public nachrichten von usern, denen wir folgen:
    followed_profiles = request.user.profile.follows.all()
    for followed_profile in followed_profiles:
        public_messages_of_user = Circle_message.objects.filter(creator=followed_profile.user, public=True)
        message_list += public_messages_of_user.all()

    (settings, created) = Settings.objects.get_or_create(owner=request.user)

    if settings.show_own_messages_on_home_screen:
        message_list += Circle_message.objects.filter(creator=request.user).all()

    message_list.sort(key=lambda m: m.created, reverse=True)

    return render(request, "logged_in/home.html", {"user": request.user,
                                                   "profile": Profile.objects.get(user=request.user.pk),
                                                   "message_list": message_list,
                                                   "circles": Circle.objects.filter(owner=request.user.pk)})


@login_required
def view_profile(request, slug):
    profile = Profile.objects.get(pk=slug)
    profile.i_am_following = request.user.profile.follows.all().filter(pk=profile.user)

    if profile == request.user.profile:
        messages.info(request, "Das ist Dein eigenes oeffentliches Profil")

    circles_im_in = Circle.objects.filter(members=request.user, owner=profile.user)

    message_list = []
    # nachrichten, die in kreisen sind, denen ich zugeteilt wurde
    for circle in circles_im_in:
        message_list += (circle.messages.all())

    # nachrichten, die keinem kreis zugeordnet sind - also public sind
    # 1. alle circles
    circles_of_user = Circle.objects.filter(owner=profile.user)
    # 2. alle public nachrichten vom user
    messages_of_user = Circle_message.objects.filter(creator=profile.user, public=True)
    message_list += (messages_of_user.all())
    message_list.sort(key=lambda m: m.created, reverse=True)

    return render(request, "logged_in/view_profile.html", {"profile": profile,
                                                           "message_list": message_list,
                                                           "user": request.user})


class EditProfileView(SuccessMessageMixin, UpdateView):
    """
    Controls the behaviour if a logged in user want to edit his profile.
    If an image is uploaded, then a smaller version of this is created.
    Returns the edit_own_profile.html rendered with a profile object.
    """
    model = Profile
    template_name = "logged_in/edit_own_profile.html"
    fields = ["gender", "description"]
    success_url = reverse_lazy("update_profile")
    success_message = "Profil wurde gespeichert"

    def get_form(self, form_class=None):
        """
        Normal form, just with an added File Upload for a picture
        :param form_class:
        :return:
        """
        form = super(EditProfileView, self).get_form(form_class)
        form.fields['image_file'] = FileField(widget=ClearableFileInput(attrs={"accept": "image/*"}))
        form.fields['image_file'].required = False
        return form

    def __create_small_picture__(request):
        """
        Generates a smaller, standard size (128x128) picture of original image with filename <o_o_image_filename>.
        Filename of smaller file is <o_o_image_filename>_sm
        If this fails, the smaller file will we removed!
        :param request:  the originial request object
        :param o_image: the filename of original image
        :return: True on success, False else
        """
        profile = request.user.profile
        outfile = profile.profile_picture_full.path + "_sm"
        try:
            im = Image.open(request.user.profile.profile_picture_full.path)
            im.thumbnail((128, 128))
            thumb_io = BytesIO()
            im.save(thumb_io, format='JPEG')
            thumb_file = InMemoryUploadedFile(thumb_io, None, 'pp.jpg', 'image/jpeg',
                                              thumb_io.getbuffer().nbytes, None)
            profile.profile_picture_small = thumb_file
            profile.save()
            return True
        except IOError:
            logging.error("Fehler beim speichern des thumbnails")
            try:
                os.remove(outfile)
            except IOError:
                pass
            return False

    def form_valid(self, form):
        """
        Handles the Image upload, verify, saving, etc.
        :param form:
        :return:
        """
        instance = form.save(commit=False)
        instance.user = self.request.user
        image_file = self.request.FILES.get('image_file', False)
        if image_file:
            imgtype = imghdr.what(image_file)
            if imgtype in ["jpeg", "png", "gif"]:
                instance.profile_picture_full = image_file
                instance.save()
                if not EditProfileView.__create_small_picture__(self.request):
                    errors = form._errors.setdefault('image_file', ErrorList())
                    messages.warning(self.request, "Bild nicht gespeichert - altes Bild wurde geloescht")
                    errors.append(
                        "Das Thumbnail konnte nicht erzeugt werden; benutzen Sie ein anderes (jpg,png,gif(nicht animiert)) Bild.")
                    return super(EditProfileView, self).form_invalid(form)
        return super(EditProfileView, self).form_valid(form)

    def get_object(self, queryset=None):
        return Profile.objects.get(user=self.request.user.pk)

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(EditProfileView, self).dispatch(request, *args, **kwargs)


class EditUserdataView(SuccessMessageMixin, UpdateView):
    """
    View to edit user data.
    Template is "edit_own_userdata.html"
    """
    model = User
    template_name = "logged_in/edit_own_userdata.html"
    fields = ["first_name", "last_name", "email"]
    success_url = "/updateuser"
    success_message = "Daten gespeichert!"

    def get_object(self, queryset=None):
        return self.request.user

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(EditUserdataView, self).dispatch(request, *args, **kwargs)


class UserSearchResultsView(ListView):
    """
    Handles the results of a user search.
    """
    model = User
    template_name = "logged_in/usersearch_results.html"
    context_object_name = "O"

    def get_queryset(self):
        ownprofile = self.request.user.profile
        ownprofile.follows_list = ownprofile.follows.all()
        usrname = self.request.GET.get("q", False)
        if usrname and len(usrname) > 0:
            userset = User.objects.filter(username__contains=usrname).order_by("username")
        else:
            userset = User.objects.all().order_by("username")
        for user in userset:
            user.i_am_following = ownprofile.follows.all().filter(pk=user)
        return {"user_list": userset, "ownprofile": ownprofile}

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(UserSearchResultsView, self).dispatch(request, *args, **kwargs)


@csrf_protect
def register(request):
    """
    Handle user registration and create profile for the user.
    use the registration form and check all the fields , with valid infos create object user and store 
    all the attributes 
    param: request
    return object of httpresponse 
    """
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password1'],
                email=form.cleaned_data['email'],
                first_name=form.cleaned_data.get('first_name', ''),
                last_name=form.cleaned_data.get('last_name', ''),
            )
            new_profile = Profile()
            new_profile.user = user
            new_profile.gender = ""
            new_profile.description = ""
            new_profile.save()
            messages.success(request, "Sie sind registriert und koennen sich nun einloggen!")
            return HttpResponseRedirect(reverse("start"))
        else:
            messages.error(request, "Sie haben ungueltige Daten angegeben!")
    else:
        form = RegistrationForm()
    variables = {
        'form': form
    }

    return render(request,
                  'guest/register.html',
                  variables,
                  )


def register_success(request):
    return render_to_response(
        'registration/success.html',
    )


@login_required
def logout(request):
    """
    Logout the current user.
    :param request:
    :return:
    """
    authlogout(request)
    messages.success(request, "Sie sind ausgeloggt!")
    return HttpResponseRedirect(reverse("start"))


def __create_dummy_pic_response__():
    """
    Creates a red dummy image, if read from disk fails, but image should be available.
    :return:
    """
    red = Image.new('RGBA', (128, 128), (255, 0, 0, 0))
    response = HttpResponse(content_type="image/jpeg")
    red.save(response, "JPEG")
    return response


@login_required
def profilepicture_full(request, slug):
    """
    Returns the full size profile image or the dummy, if not present/on IOError.
    :param request:
    :param slug:
    :return:
    """
    try:
        profile = Profile.objects.get(pk=slug)
    except ObjectDoesNotExist:
        return __create_dummy_pic_response__()
    if profile.profile_picture_full:
        image = profile.profile_picture_full.path
    else:
        image = Profile.objects.get(user__username="SYSTEM").profile_picture_full.path
    try:
        with open(image, "rb") as f:
            return HttpResponse(f.read(), content_type="image/jpeg")
    except IOError:
        return __create_dummy_pic_response__()


@login_required
def profilepicture_small(request, slug):
    """
    Returns the standard 128x128 profile image or the dummy if not present/on IO error.
    :param request:
    :param slug:
    :return:
    """
    try:
        profile = Profile.objects.get(pk=slug)
    except ObjectDoesNotExist:
        return __create_dummy_pic_response__()
    if profile.profile_picture_small:
        image = profile.profile_picture_small.path
    else:
        image = Profile.objects.get(user__username="SYSTEM").profile_picture_small.path
    try:
        with open(image, "rb") as f:
            return HttpResponse(f.read(), content_type="image/jpeg")
    except IOError:
        return __create_dummy_pic_response__()


def password_change(request):
    if request.method == "POST":
        messages.info(request, "Wenn keine Fehler angezeigt wurden, wurde das Passwort geaendert")
    return _pw_change_(request,
                       template_name='logged_in/change_password.html',
                       post_change_redirect=reverse("home"))


def impressum(request):
    if request.user.is_authenticated():
        return render(request, "logged_in/impressum.html")
    else:
        return render(request, "guest/impressum.html")


import hashlib
from os import urandom


def reset_password(request):
    if request.method == "POST":
        username = request.POST.get("username", False)
        email = request.POST.get("email", False)
        if not (username or email):
            return render(request, "forgot_password/forgot_password.html", {"errors": "Benutzername oder EMail fehlen"})
        try:
            user = User.objects.get(username=username, email=email)
        except ObjectDoesNotExist:
            return render(request, "forgot_password/forgot_password.html",
                          {"errors": "Benutzername oder Email stimmen nicht"})
        new_pwd = hashlib.sha1()
        new_pwd.update(urandom(64))
        send_mail("Dein neues Password",
                  message= "Deine neues Passwort lautet: '%s'. Log Dich ein, um es direkt zu aendern!" % new_pwd,
                  html_message="<html><h3>Dein neues Passwort:</h3>"
                               "<p>%s</p><br />"
                               "<a href='%s'>Log Dich ein und aendere es!</a>."
                               "</html>" % (new_pwd, reverse("start"),),from_email="PasswortAenderung@vps146949.ovh.net", recipient_list=(user.email,))
        return render(request, "forgot_password/message_password_sent.html")
    return render(request, "forgot_password/forgot_password.html")
