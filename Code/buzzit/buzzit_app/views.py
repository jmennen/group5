from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.db.models import QuerySet
from django.contrib.messages.views import SuccessMessageMixin
from django.forms.utils import ErrorList
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, render_to_response
from django.template import RequestContext
from django.utils.decorators import method_decorator
from django.utils.http import is_safe_url
from django.views.decorators.csrf import csrf_protect
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView,DeleteView,CreateView,FormView
from django.views.generic.list import ListView
from .forms import RegistrationForm
from buzzit_models.models import *
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.urlresolvers import reverse,reverse_lazy
from django.contrib.auth import login, logout as authlogout
from django.contrib.auth.views import password_change as _pw_change_
import logging
from django.forms.fields import FileField, ClearableFileInput, CharField, EmailField
from django.core.exceptions import ObjectDoesNotExist
from PIL import Image
import imghdr
import os


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
            pass  # TODO: was passiert dann?
        return HttpResponseRedirect(reverse("home"))
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user:
                login(request, user)
                if not request.user.is_active:
                    pass  # TODO: dann?
                redirect_to = request.REQUEST.get("next", False)
                if (redirect_to):
                    if not is_safe_url(url=redirect_to, host=request.get_host()):
                        return HttpResponseRedirect(reverse("home"))
                    return HttpResponseRedirect(redirect_to)
                return HttpResponseRedirect(reverse("home"))
            else:
                pass  # TODO: fehler beim login melden
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
    return render(request, "logged_in/home.html", {"user": request.user,
                                                   "profile": Profile.objects.get(user=request.user)})


class ProfileView(DetailView):
    """
    Controls the behaviour, if a logged in user wants to show a users profile.
    Returns the view_profile.html template rendered with a "profile" object.
    """
    model = Profile
    template_name = "logged_in/view_profile.html"
    slug_field = "user"

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(ProfileView, self).dispatch(request, *args, **kwargs)


class EditProfileView(UpdateView):
    """
    Controls the behaviour if a logged in user want to edit his profile.
    If an image is uploaded, then a smaller version of this is created.
    Returns the edit_own_profile.html rendered with a profile object.
    """
    model = Profile
    template_name = "logged_in/edit_own_profile.html"
    fields = ["gender", "description"]
    success_url = "/updateprofile"

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

    def __create_small_picture__(request, o_image_filename):
        """
        Generates a smaller, standard size (128x128) picture of original image with filename <o_o_image_filename>.
        Filename of smaller file is <o_o_image_filename>_sm
        If this fails, the smaller file will we removed!
        :param request:  the originial request object
        :param o_image_filename: the filename of original image
        :return: True on success, False else
        """
        outfile = o_image_filename + "_sm"
        try:
            im = Image.open(o_image_filename)
            im.thumbnail((128, 128))
            im.save(outfile, "JPEG")
            im.close()
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
        image_file_name = "pp/pp_" + self.request.user.username
        if image_file:
            imgtype = imghdr.what(image_file)
            if imgtype in ["jpeg", "png", "gif"]:
                try:
                    f = open(image_file_name, "xb")
                except FileExistsError:
                    f = open(image_file_name, "wb")
                for chunk in image_file.chunks():
                    f.write(chunk)
                f.close()
                if not EditProfileView.__create_small_picture__(self.request, image_file_name):
                    os.remove(image_file_name)
                    errors = form._errors.setdefault('image_file', ErrorList())
                    errors.append(
                        "Das Thumbnail konnte nicht erzeugt werden; benutzen Sie ein anderes (jpg,png,gif(nicht animiert)) Bild.")
                    return super(EditProfileView, self).form_invalid(form)
                else:
                    instance.profile_picture = reverse("profile_picture_small", kwargs={"slug": self.request.user.pk})
                    instance.save()
        return super(EditProfileView, self).form_valid(form)

    def get_object(self, queryset=None):
        return Profile.objects.get(user=self.request.user)

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(EditProfileView, self).dispatch(request, *args, **kwargs)


class EditUserdataView(UpdateView):
    """
    View to edit user data.
    Template is "edit_own_userdata.html"
    """
    model = User
    template_name = "logged_in/edit_own_userdata.html"
    fields = ["first_name", "last_name", "email"]
    success_url = "/updateuser"

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

    def get_queryset(self):
        usrname = self.request.GET.get("q", False)
        if usrname and len(usrname) > 0:
            userset = User.objects.filter(username__contains=usrname)
        else:
            userset = User.objects.all()
        for user in userset:
            user.profile = Profile.objects.get(user=user)
        return userset

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
            new_profile.profile_picture = "https://placehold.it/128x128"
            new_profile.gender = ""
            new_profile.description = ""
            new_profile.save()
            return HttpResponseRedirect(reverse("start"))
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
        username = User.objects.get(pk=slug).username
    except ObjectDoesNotExist:
        return __create_dummy_pic_response__()
    image = "pp/pp_" + username
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
        username = User.objects.get(pk=slug).username
    except ObjectDoesNotExist:
        return __create_dummy_pic_response__()
    image = "pp/pp_" + username + "_sm"
    try:
        with open(image, "rb") as f:
            return HttpResponse(f.read(), content_type="image/jpeg")
    except IOError:
        return __create_dummy_pic_response__()


def password_change(request):
    return _pw_change_(request,
                       template_name='logged_in/change_password.html',
                       post_change_redirect=reverse("home"))


def impressum(request):
    if request.user.is_authenticated():
        return render(request, "logged_in/impressum.html")
    else:
        return render(request, "guest/impressum.html")

class circleOverView(ListView):
    model = Circle
    template_name = "logged_in/circle_overview.html"

    def cirlcle(self):
        return Circle.objects.all()

class createCircleView(CreateView,SuccessMessageMixin):
    """
    erstellt neue Kreise,dies passiert wie deletecircle auch auf der Seite circleoverview

    """
    model = Circle
    template_name = "logged_in/circle_overview.html"
    fields = ['name']
    success_message = "%(name)s die Kreise erfolgreich erstellt"
    success_url = reverse_lazy("createcircle")
    #ob man kreise mit selbem Name erstellen darf
    def form_valid(self, form):
        self.object = form.save(commit=False)
        #form.instance.owner = self.request.user
  #      try:
   #         form.instance.name = self.cleand_data['name']
    #    except self.cleaned_data['name']

#            raise V
        form.instance.owner = self.request.user
        form.save()
        # Another computing etc
        self.object.save()
        return super(createCircleView, self).form_valid(form)
    """
    success_message = "%(name)s die Kreise erfolgreich erstellt"

    def clean_name(self):
        name = self.cleaned_data['name']
        if self.object.filter(name=name).exit():
            raise ValidationError
    def get_success_url(self):
       # if self.request.form.is_valid():
           # circle = Circle(Circle.owner = self.request.user, Circle.name = self.request.form.cleaned.data['name'])

        return reverse("createcircle", kwargs={'pk': self.object.owner} )
    #def dispatch(self, request, *args, **kwargs):
        #return super(createCircle, self).dispatch(request, *args, **kwargs)
    """
class deleteCircleView(DeleteView,SuccessMessageMixin):
    """
    wenn Kreis user und Nachricte enthaelt, was passiert?
    wenn nicht, einfach loeschen

    Nachdem loeschen sind Nachrichte noetig ?
    """
    model = Circle
    success_message = "%(name)s die Kreise erfolgreich geloescht"
    success_url = reverse_lazy("circle-list")  #url anpassen
