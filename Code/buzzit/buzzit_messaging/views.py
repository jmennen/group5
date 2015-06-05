from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render
from django.utils.datetime_safe import datetime
from django.utils.decorators import method_decorator
from django.views.generic import ListView, UpdateView, CreateView, DeleteView
from django.http import HttpResponseRedirect
from buzzit_models.models import *
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse, reverse_lazy

class BeingFollowedByView(ListView):
    model = Profile
    template_name = "buzzit_messaging/logged_in/being_followed_by_userlist.html"

    def get_queryset(self):
        logged_in_user = self.request.user
        return Profile.objects.filter(follows=logged_in_user.pk)

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


class CreateCircleView(CreateView, SuccessMessageMixin):
    model = Circle
    success_message = "Kreis %(name)s erfolgreich erstellt"

    def get_success_url(self):
        reverse("circle_details", {"slug" : self.object.pk})

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(CreateCircleView, self).dispatch(request, *args, **kwargs)


class CircleOverviewView(ListView):
    model = Circle
    template_name = "buzzit_messaging/logged_in/circle_overview.html"

    def get_queryset(self):
        logged_in_user = self.request.user.pk
        return Circle.objects.filter(owner=logged_in_user.pk)

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(CircleOverviewView, self).dispatch(request, *args, **kwargs)


@login_required
def listfollows(request):
    # list of profile
    profiles_ids = Profile.objects.get(user=request.user.id).follows
    profiles = Profile.objects.filter(pk__in = profiles_ids)
    return render(request, "buzzit_messaging/logged_in/following_userlist.html", {"profile": profiles})


class PostCirclemessageView(CreateView, SuccessMessageMixin):
    model = Circle_message
    fields = ["text"]
    success_message = "Kreisnachricht gespeichert"
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        form.creator = self.request.user.pk
        form.created = datetime.now()
        return super(PostCirclemessageView, self).form_valid(form)

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(PostCirclemessageView, self).dispatch(request, *args, **kwargs)


class DeleteCirclemessageView(DeleteView):
    model = Circle_message


class RemoveCircle(DeleteView):
    model = Circle


@login_required
def add_user_to_circle(request, user_id, circle_id):
    pass


@login_required
def remove_user_from_circle(request, user_id, circle_id):
    pass


@login_required()
def follow(request, user_id):
    try:
        follow_user = Profile.objects.get(pk=user_id)
    except ObjectDoesNotExist:
        # user to follow does not exist
        return HttpResponseRedirect(reverse_lazy('home'))
    try:
        my_profile = Profile.objects.get(pk=request.user.pk)
    except ObjectDoesNotExist:
        # logged in user has no profile
        return HttpResponseRedirect(reverse_lazy('home'))
    my_profile.follows.add(follow_user)
    return HttpResponseRedirect(reverse_lazy('home'))


@login_required()
def unfollow(request, user_id):
    # TODO: exceptions für nicht gefundene user usw (wie follow())
    unfollow_user = Profile.objects.get(pk=user_id)
    my_profile = Profile.objects.get(pk=request.user)
    circles_of_unfollowed_user = Circle.objects.filter(owner=unfollow_user.pk, members=my_profile.pk)
    for circle in circles_of_unfollowed_user:
        circle.members.remove(my_profile)
    my_profile.follows.remove(unfollow_user)
    return HttpResponseRedirect(reverse_lazy('home'))