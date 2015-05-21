from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import DetailView, UpdateView, ListView
from buzzit_models.models import *
from django.contrib.auth.forms import UserCreationForm
from django.core.urlresolvers import reverse

@login_required
class ProfileView(DetailView):
    model = Profile

@login_required
class EditProfileView(UpdateView):
    model = Profile

@login_required
class EditUserdataView(UpdateView):
    model = User

@login_required
class UserSearchResultsView(ListView):
    model = User

def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('start'))
    else:
        form = UserCreationForm()
    return render(request, "guest/register.html", {'form' : form})