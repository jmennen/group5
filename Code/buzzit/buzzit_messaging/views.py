import string
from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.middleware.common import logger
from django.shortcuts import render
from django.utils.datetime_safe import datetime
from django.utils.decorators import method_decorator
from django.views.generic import ListView, UpdateView, CreateView, DeleteView
from django.http import HttpResponseRedirect, JsonResponse
from buzzit_models.models import *
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse, reverse_lazy
import django.contrib.messages as messages
import logging


@login_required
def beingFollowedByView(request):
    return render(request, "buzzit_messaging/logged_in/being_followed_by_userlist.html",
                  {
                      "profile_list": Profile.objects.filter(follows=request.user.pk),
                      "circles": Circle.objects.filter(owner=request.user)
                  })


@login_required
def circleDetails(request, slug):
    return render(request, "buzzit_messaging/logged_in/circle_details.html",
                  {"circle": Circle.objects.get(owner=request.user, pk=slug),
                   "followers": Profile.objects.filter(follows=request.user.profile)})


class CreateCircleView(CreateView, SuccessMessageMixin):
    model = Circle
    success_message = "Kreis %(name)s erfolgreich erstellt"
    fields = ["name"]

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super(CreateCircleView, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy("circle_details", args=(self.object.pk,))

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(CreateCircleView, self).dispatch(request, *args, **kwargs)


class CircleOverviewView(ListView):
    model = Circle
    template_name = "buzzit_messaging/logged_in/circle_overview.html"

    def get_queryset(self):
        logged_in_user = self.request.user
        return Circle.objects.filter(owner=logged_in_user.pk)

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(CircleOverviewView, self).dispatch(request, *args, **kwargs)


@login_required
def listfollows(request):
    # list of profile
    my_profile = request.user.profile
    return render(request,
                  "buzzit_messaging/logged_in/following_userlist.html",
                  {"profile": my_profile, "follows": my_profile.follows.all()}
                  )


class PostCirclemessageView(CreateView, SuccessMessageMixin):
    model = Circle_message
    fields = ["text"]
    success_message = "Kreisnachricht gespeichert"
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        form.instance.creator = self.request.user
        form.instance.created = datetime.now()
        return super(PostCirclemessageView, self).form_valid(form)

    def get_success_url(self):
        # nachricht in die circles
        # TODO: Wenn exceptions auftreten nachricht loeschen oder so
        circle_ids = self.request.POST.getlist("circles", [])
        for circle_id in circle_ids:
            logging.getLogger(__name__).error(circle_id)
            circle = Circle.objects.get(pk=circle_id)
            circle.messages.add(self.object.id)
        return self.success_url

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(PostCirclemessageView, self).dispatch(request, *args, **kwargs)


@login_required
def delete_circle_message(request, message_id):
    try:
        message_to_del = Circle_message.objects.get(pk=message_id)
    except ObjectDoesNotExist:
        messages.error(request, "Kreisnachricht existiert nicht")
        return HttpResponseRedirect(reverse_lazy('home'))
    if request.user != message_to_del.creator:
        messages.error(request, "Diese Kreisnachricht duerfen Sie nicht loeschen")
        return HttpResponseRedirect(reverse_lazy('home'))
    message_to_del.delete()
    messages.success(request, "Nachricht geloescht")
    return HttpResponseRedirect(reverse_lazy('home'))


class DeleteCirclemessageView(DeleteView):
    model = Circle_message

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(PostCirclemessageView, self).dispatch(request, *args, **kwargs)


class RemoveCircleView(DeleteView, SuccessMessageMixin):
    """
    pick up the circle primary key from template and remove the circle with the given object
    auto-removes the relations circle-members
    """
    model = Circle
    success_message = "%(name)s die Kreise erfolgreich geloescht"
    slug_field = "id"
    success_url = reverse_lazy("circle_overview")

    def get(self, *args, **kwargs):
        return self.post(*args, **kwargs)


def add_user_to_circles(request, user_id):
    circle_ids = request.POST.getlist("circles")
    if len(circle_ids) < 1:
        messages.error(request, "Keine Kreise angegeben")
        return HttpResponseRedirect(reverse_lazy('my_followers'))
    try:
        user = User.objects.get(pk=user_id)
    except ObjectDoesNotExist:
        messages.error(request, "User mit id %s existiert nicht" % user_id)
        return HttpResponseRedirect(reverse_lazy('home'))
    for circle_id in circle_ids:
        try:
            circle = Circle.objects.get(pk=circle_id)
        except ObjectDoesNotExist:
            messages.error(request, "Kreis mit id %s existiert nicht" % circle_id)
            return HttpResponseRedirect(reverse_lazy('home'))
        circle.members.add(user)
        messages.success(request, "Dem Kreis %s wurde der User %s hinzugefuegt" % (circle.name, user.username))
    return HttpResponseRedirect(reverse_lazy('my_followers'))


@login_required
def add_users_to_circle(request, circle_id):
    user_ids = request.POST.getlist("add_members")
    for user_id in user_ids:
        try:
            follow_user = Profile.objects.get(pk=user_id)
        except ObjectDoesNotExist:
            # user to follow does not exist
            messages.error(request, "User mit id %s existiert nicht" % user_id)
            return HttpResponseRedirect(reverse_lazy('home'))
        try:
            my_profile = Profile.objects.get(pk=request.user)
        except ObjectDoesNotExist:
            # logged in user has no profile
            return HttpResponseRedirect(reverse_lazy('home'))
        try:
            chosen_circle = Circle.objects.get(pk=circle_id)
        except ObjectDoesNotExist:
            # circle does not exist
            messages.error(request, "Kreis existiert nicht")
            return HttpResponseRedirect(reverse_lazy('home'))
        try:
            check_follow_status = follow_user.follows.get(pk=request.user)
        except ObjectDoesNotExist:
            # user is not a follower
            messages.error(request, "Der User ist kein Follower")
            return HttpResponseRedirect(reverse_lazy('home'))
        chosen_circle.members.add(follow_user.user)
    messages.success(request, "User wurden dem Kreis hinzugefuegt")
    return HttpResponseRedirect(reverse_lazy("circle_details", args=(circle_id,)))


@login_required
def remove_user_from_circle(request, user_id, circle_id):
    try:
        follow_user = Profile.objects.get(pk=user_id)
    except ObjectDoesNotExist:
        # user to follow does not exist
        messages.error(request, "User existiert nicht")
        return HttpResponseRedirect(reverse_lazy('home'))
    try:
        my_profile = Profile.objects.get(pk=request.user)
    except ObjectDoesNotExist:
        # logged in user has no profile
        return HttpResponseRedirect(reverse_lazy('home'))
    try:
        chosen_circle = Circle.objects.get(pk=circle_id)
    except ObjectDoesNotExist:
        # circle does not exist
        messages.error(request, "Kreis existiert nicht")
        return HttpResponseRedirect(reverse_lazy('home'))
    chosen_circle.members.remove(follow_user.user)
    messages.success(request, "User %s wurde aus Kreis %s entfernt" % (follow_user.user.username, chosen_circle.name))
    return HttpResponseRedirect(reverse_lazy('circle_details', kwargs={'slug': circle_id}))


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
    my_profile.follows.add(follow_user.pk)
    messages.success(request, "Du folgst jetzt %s" % follow_user.user.username)
    return HttpResponseRedirect(reverse_lazy('home'))


@login_required()
def unfollow(request, user_id):
    # TODO: exceptions fuer nicht gefundene user usw (wie follow())
    unfollow_user = Profile.objects.get(pk=user_id)
    my_profile = Profile.objects.get(pk=request.user.pk)
    # take circles of unfollowed user
    circles_of_unfollowed_user = Circle.objects.filter(owner=unfollow_user.pk, members=my_profile.pk)
    for circle in circles_of_unfollowed_user:
        circle.members.remove(my_profile.pk)
    my_profile.follows.remove(unfollow_user.pk)
    messages.success(request, "Du folgst %s nicht mehr" % unfollow_user.user.username)
    return HttpResponseRedirect(reverse_lazy('home'))


@login_required
def direct_messages_overview(request):
    """
    Overview of all direct messages.
    Returns two objects:
    1. directmessage_list : a list of all chats with one specific user
    2. systemmessages : a list of all system messages

    :param request:
    :return:
    """
    pass


@login_required
def direct_messages_details(request, sender_id):
    """
    One specific chat. So this filters all messages from one specific sender.
    Returns one object: directmessage_list, where sender was specified by user_id
    and receiver is the logged in user and vice versa.
    :param request:
    :return:
    """
    pass


@login_required
def repost_circlemessage(request, original_message_id):
    """
    Creates a new post with referencing to the old one specified by original_message_id.
    The new post  has its own text and all data, but the field "original_post" is filled.
    :param request:
    :param original_message_id:
    :return:
    """
    pass


@login_required
def answer_to_circlemessage(request, message_id):
    """
    Answer to a message specified by message_id.
    :param request:
    :param message_id:
    :return:
    """
    pass


@login_required
def one_circlemessage(request, message_id):
    """
    Gives the ability to view details about the circlemessage by message_id.
    :param request:
    :param message_id:
    :return:
    """
    pass


@login_required
def information_about_new_directmessages(request):
    """
    The function, that answers the client polling.
    Only allowed method is GET.
    Returns JSON Data like
    {
        "new_notifications" : <count of new notifications>
    }
    So if <count of new notifications> is > 0, the logged in user has new notifications.
    :param request:
    :return:
    """
    notifications_count = Directmessage.objects.filter(receiver=request.user, read=False).count()
    return JsonResponse({"new_notifications": notifications_count})


@login_required
def search_user_json(request, query):
    users = User.objects.filter(username__contains=query).only('username')
    usernamelist = []
    for user in users:
        usernamelist.append(user.username)
    return JsonResponse({"symbol": "@", "list": usernamelist}, safe=False, )


@login_required
def search_theme_json(request, query):
    themes = Theme.objects.filter(username__contains=query).only('name')
    themenamelist = []
    for user in themes:
        themenamelist.append(user.username)
    return JsonResponse({"symbol": "#", "list": themenamelist}, safe=False, )
    pass
