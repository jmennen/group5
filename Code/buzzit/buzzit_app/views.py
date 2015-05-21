from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
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
                    pass # TODO: dann?
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
            form.save()
            return HttpResponseRedirect(reverse('home'))
    else:
        form = UserCreationForm()
    return render(request, "guest/register.html", {'form': form})


def logout(request):
    authlogout(request)
    return HttpResponseRedirect(reverse("start"))