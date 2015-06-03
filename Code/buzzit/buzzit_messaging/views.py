from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.datetime_safe import datetime
from django.utils.decorators import method_decorator
from django.views.generic import ListView, UpdateView, CreateView, DeleteView
from django.http import HttpResponseRedirect
from buzzit_models.models import *


class BeingFollowedByView(ListView):
    model = Profile
    template_name = "buzzit_messaging/logged_in/being_followed_by_userlist.html"

    def get_queryset(self):
        logged_in_user = self.request.user
        return Profile.objects.filter(follows=logged_in_user)

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(BeingFollowedByView, self).dispatch(request, *args, **kwargs)


class CircleDetailsView(UpdateView):
    model = Circle
    template_name = "buzzit_messaging/logged_in/circle_details.html"

    def get_object(self, queryset=None):
        logged_in_user = self.request.user
        return Circle.objects.get(owner=logged_in_user, pk=self.request.kwargs.get('slug'))

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(CircleDetailsView, self).dispatch(request, *args, **kwargs)


class CreateCircleView(CreateView):
    model = Circle


class CircleOverviewView(ListView):
    model = Circle
    template_name = "buzzit_messaging/logged_in/circle_overview.html"

    def get_queryset(self):
        logged_in_user = self.request.user
        return Circle.objects.filter(owner=logged_in_user)

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(CircleOverviewView, self).dispatch(request, *args, **kwargs)


@login_required
def listfollows(request):
    profile = Profile.objects.get(user=request.user)
    return render(request, "buzzit_messaging/logged_in/following_userlist.html", {"profile": profile})


class PostCirclemessageView(CreateView):
    model = Circle_message
    fields = ["text"]

    def form_valid(self, form):
        form.creator = self.request.user
        form.created = datetime.now()
        return super(PostCirclemessageView, self).form_valid(form)


class DeleteCirclemessageView(DeleteView):
    model = Circle_message


class RemoveCircle(DeleteView):
    model = Circle


@login_required()
def follow(request, user_id):
    follow_user = Profile.objects.get(pk=user_id)
    my_profile = Profile.objects.get(pk=request.user)
    my_profile.follows.add(follow_user)
    return HttpResponseRedirect('home')


@login_required()
def unfollow(request, user_id):
    unfollow_user = Profile.objects.get(pk=user_id)
    my_profile = Profile.objects.get(pk=request.user)
    my_profile.follows.remove(unfollow_user)
    return HttpResponseRedirect('home')