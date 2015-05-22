from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.utils.http import is_safe_url
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView
from django.views.generic.list import ListView
from buzzit_models.models import *
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.urlresolvers import reverse
from django.contrib.auth import login, logout as authlogout
import logging
from django.forms.fields import FileField
from django.core.exceptions import ObjectDoesNotExist
from PIL import Image


def start(request):
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
    return render(request, "logged_in/home.html", {"user": request.user})


class ProfileView(DetailView):
    model = Profile
    template_name = "logged_in/view_profile.html"
    slug_field = "user"

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(ProfileView, self).dispatch(request, *args, **kwargs)


class EditProfileView(UpdateView):
    model = Profile
    template_name = "logged_in/edit_own_profile.html"
    fields = ["gender", "description"]
    success_url = "/updateprofile"

    def get_form(self, form_class=None):
        form = super(EditProfileView, self).get_form(form_class)
        form.fields['image_file'] = FileField()
        form.fields['image_file'].required = False
        return form

    def __create_small_picture__(request, o_image_filename):
        outfile = o_image_filename + "_sm"
        try:
            im = Image.open(o_image_filename)
            im.thumbnail((128,128))
            im.save(outfile, "JPEG")
        except IOError:
            logging.error("Nope")

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.user = self.request.user
        image_file = self.request.FILES.get('image_file', False)
        image_file_name = "pp/pp_" + self.request.user.username
        if image_file:
            try:
                f = open(image_file_name, "xb")
            except FileExistsError:
                f = open(image_file_name, "wb")
            for chunk in image_file.chunks():
                f.write(chunk)
            f.close()
            EditProfileView.__create_small_picture__(self.request, image_file_name)
            instance.profile_picture = reverse("profile_picture_small", kwargs={"slug": self.request.user.pk})
            instance.save()
            # TODO: datei speichern und public path in instance speichern
        return super(EditProfileView, self).form_valid(form)

    def get_object(self, queryset=None):
        return Profile.objects.get(user=self.request.user)

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(EditProfileView, self).dispatch(request, *args, **kwargs)


class EditUserdataView(UpdateView):
    model = User
    template_name = "logged_in/edit_own_userdata.html"
    fields = ["first_name", "last_name", "email"]

    def get_object(self, queryset=None):
        return self.request.user

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(EditUserdataView, self).dispatch(request, *args, **kwargs)


class UserSearchResultsView(ListView):
    model = User
    template_name = "logged_in/usersearch_results.html"


    def get_queryset(self):
        return User.objects.filter(username__contains=self.kwargs.get("slug", ""))

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(UserSearchResultsView, self).dispatch(request, *args, **kwargs)


def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            # erzeuge profil:
            profile = Profile()
            profile.user = new_user
            profile.save()
            return HttpResponseRedirect(reverse('home'))
    else:
        form = UserCreationForm()
    return render(request, "guest/register.html", {'form': form})


@login_required
def logout(request):
    authlogout(request)
    return HttpResponseRedirect(reverse("start"))


def __create_dummy_pic_response__():
    red = Image.new('RGBA', (64, 64), (255, 0, 0, 0))
    response = HttpResponse(content_type="image/jpeg")
    red.save(response, "JPEG")
    return response


@login_required
def profilepicture_full(request, slug):
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