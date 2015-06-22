import string
from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.middleware.common import logger
from django.shortcuts import render
from django.utils.datetime_safe import datetime
from django.utils.decorators import method_decorator
from django.views.generic import ListView, UpdateView, CreateView, DeleteView
from django.http import HttpResponseRedirect
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

def RemoveCircleView(request, slug):
    """
    pick up the circle primary key from template and remove the circle with the given object
    auto-removes the relations circle-members
    """
    try:
        circle_to_del = Circle.objects.get(pk = slug)
        messages_to_del = circle_to_del.messages.all()
        for m in messages_to_del:
            if (not (Circle.objects.filter(messages = m).count() > 1)):
                # TODO: achtung - wenn nachricht retweetet, dann nicht löschen!!
                # if not (Circle_message.objects.filter(original_message = m).count() > 0):
                    # antworten müssen gelöscht werden:
                    #Circle_message.objects.filter(answer_to = m).delete()
                m.delete() # TODO: muss später eingerückt werden
        circle_to_del.delete()
    except Exception:
        messages.error(request, "Fehler beim loeschen")
    return HttpResponseRedirect(reverse("circle_overview"))


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

@login_required()
class answerToCircleMessageView(CreateView,SuccessMessageMixin):
    """
    create answer for circle messages
    """
    model = Circle_message
    fields = ['text']
    success_message = "du hast darauf geantwortet"
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        form.instance.creator = self.request.user
        form.instance.created = datetime.now()
        original_id = self.request.kwargs.get("message_id")
        try:
            form.instance.answer_to = Circle_message.objects.get(pk=original_id) #the curcle message key which the message answered to
        except ObjectDoesNotExist:
            messages.error(self.request,"Nachticht existiert nicht.")
            return HttpResponseRedirect(reverse_lazy("home"))
        return super(answerToCircleMessageView, self).form_valid(form)

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(answerToCircleMessageView, self).dispatch(request, *args, **kwargs)


"""
aternative function to answer circle message

def answertocirclemessage(request,answertocirclemessage_id):

    try:
        messageanswerto = Circle_message.objects.get(pk=answertocirclemessage_id)
    except ObjectDoesNotExist:
        # message to answer does not exist
        messages.error(request,"Die Nachrichte, worauf du antwortest, existiert nicht mehr")
        return HttpResponseRedirect(reverse_lazy('home'))

    answer = Circle_message() # so create a new object
    answer.created = datetime.now()
    answer.creator = request.user
    answer.answer_to.add(messageanswerto)
    messages.info(request,"Du hast auf die Nachtichte geantwortet")
    return  HttpResponseRedirect(reverse_lazy('home'))
"""

@login_required()
class retweet(CreateView,SuccessMessageMixin):
    """
    add retweet to the circle messages
    """
    model = Circle_message
    fields = ['text']
    success_url = reverse_lazy("home")
    success_message = "du hast etwas retweetet"

    def form_valid(self, form):
        form.instance.creator = self.request.user
        form.instance.created = datetime.now()
        try:
            original_id = self.request.kwargs.get("message_id") # original massage id from url
            original_message = Circle_message.objects.get(pk=original_id)
        except ObjectDoesNotExist:
            messages.error(self.request,"Originale Nachricht existiert nicht")
            return HttpResponseRedirect(reverse_lazy("home"))

        form.instance.original_message = original_message
        cirle_which_currentUser_belongs_to = Circle.objects.get(members = self.request.user) # get the circle which current user belongs to
        cirle_which_currentUser_belongs_to.messages.add(form.instance) # add retweet as circle message to the circle
        return super(retweet, self).form_valid(form)

    def get_success_url(self):
        # obtain circle key from request object and add anwsers to this circle

        circle_ids = self.request.POST.getlist("circles", [])
        for circle_id in circle_ids:
            circle = Circle.objects.get(pk=circle_id)
            circle.messages.add(self.object.id)
        return self.success_url

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(retweet, self).dispatch(request, *args, **kwargs)


@login_required()
def showPostToTheTheme(request,theme):
    """
    klick on theme and show all the posts,check if the theme exits

    filter message which man should see
    :param request:
    :param theme:
    :return:
    """
    circle_in_which_i_am_a_member = []
    all_posts_which_i_can_see = []
    posts = []

    try:
        theme = Theme.objects.get(pk = theme.name)
    except ObjectDoesNotExist:
        messages.error(request,"Das gewaehlte Thema existiert nicht mehr")
        return HttpResponseRedirect(reverse_lazy("home"))

    try:
        circle_in_which_i_am_a_member = Circle.objects.filter(members = request.user.pk) # get the circle in which i am a member
        for circle in circle_in_which_i_am_a_member:
            all_posts_which_i_can_see += (circle.messages.all())

        posts = all_posts_which_i_can_see.objects.filter(themes = theme)  # might takes a while because of the posts list
    except ObjectDoesNotExist:
        messages.error(request,"Du hast noch keine Kreise")
    return render(request,"home",{"posts_list":posts})

class postDetailsView(ListView,SuccessMessageMixin):

    """
    show all the circle messge to the given message
    """
    model = Circle_message
    template_name = "buzzit_messaging/logged_in/post_details.html"

    def get_queryset(self):

        currentcirclemessage = self.request.kwargs.get("circlemessage_id")
        return Circle_message.objects.filter(answer_to = currentcirclemessage).order_by('username')

    def dispatch(self, request, *args, **kwargs):
        return super(postDetailsView, self).dispatch(request,*args,**kwargs)
