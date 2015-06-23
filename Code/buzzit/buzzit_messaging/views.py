from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render
from django.utils.datetime_safe import datetime
from django.utils.decorators import method_decorator
from django.views.generic import ListView, CreateView, DeleteView
from django.http import HttpResponseRedirect, JsonResponse
from buzzit_models.models import *
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse, reverse_lazy
import django.contrib.messages as messages
import json
from bleach import clean as html_clean


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


@login_required
def postCirclemessage(request):
    if request.method == "POST":
        newPost = Circle_message()
        ans = request.POST.get("answer_to", False)
        rep = request.POST.get("original_id", False)
        try:
            if ans:
                newPost.answer_to = Circle_message.objects.get(pk=ans)
            if rep:
                newPost.original_message = Circle_message.objects.get(pk=rep)
        except ObjectDoesNotExist:
            messages.error(request, "Fehler")
            return HttpResponseRedirect(reverse("home"))
        if newPost.original_message:
            if newPost.original_message.original_message:
                newPost.original_message = newPost.original_message.original_message
            if newPost.answer_to:
                messages.error(request, "Antworten koennen nicht repostet werden")
                return HttpResponseRedirect(reverse("home"))
        newPost.creator = request.user
        newPost.created = datetime.now()
        newPost.text = html_clean(request.POST.get("text"), tags=[])
        if len(newPost.text) < 1:
            messages.error("Es wurde kein Text angegeben")
            return HttpResponseRedirect(reverse("home"))
        newPost.save()  # save, to generate primary key to use RELs

        # now that we have a pk in the newPost, we can push it to the circles
        # or mark it as public if no circles were given
        circle_ids = request.POST.getlist("circles", [])
        if len(circle_ids) > 0:
            # not public
            for circle_id in circle_ids:
                circle = Circle.objects.get(pk=circle_id)
                circle.messages.add(newPost)
        else:
            # public
            newPost.public = True

        # add mentions, that were submitted
        # ignore users, that are not registered
        mentions = json.loads(request.POST.get("mentions", "[]"))
        for mention in mentions:
            try:
                user_mentioned = User.objects.get(username=mention["name"])
            except ObjectDoesNotExist:
                continue
            # inform mentioned user about mention
            notification = Directmessage()
            notification.created = datetime.now()
            notification.creator = User.objects.get(username="SYSTEM")
            notification.receiver = user_mentioned
            notification.text = "Du wurdest in einem Post erwaehnt: <POST:%s>" % newPost.id
            notification.save()
            newPost.mentions.add(user_mentioned)

        # add themes, that were submitted
        # create not found themes
        themes = json.loads(request.POST.get("themes", "[]"))
        for theme in themes:
            theme["name"] = html_clean(theme["name"], tags=[])
            theme_mentioned, created = Theme.objects.get_or_create(pk=theme["name"])
            if created:
                messages.info(request, "Du hast ein neues Thema erstellt: %s" % theme_mentioned.name)
            newPost.themes.add(theme_mentioned)

        # save all changes
        newPost.save()

        return HttpResponseRedirect(reverse("home"))
    return render(request, "buzzit_models/circle_message_form.html")


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
    answers = Circle_message.objects.filter(answer_to=message_to_del)
    # TODO entscheiden was mit retweets passiert
    answers.delete()
    message_to_del.delete()
    messages.success(request, "Nachricht geloescht")
    return HttpResponseRedirect(reverse_lazy('home'))


class DeleteCirclemessageView(DeleteView):
    model = Circle_message

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(DeleteCirclemessageView, self).dispatch(request, *args, **kwargs)


def RemoveCircleView(request, slug):
    """
    pick up the circle primary key from template and remove the circle with the given object
    auto-removes the relations circle-members
    """
    try:
        circle_to_del = Circle.objects.get(pk=slug)
        messages_to_del = circle_to_del.messages.all()
        for m in messages_to_del:
            if (not (Circle.objects.filter(messages=m).count() > 1)):
                # TODO: achtung - wenn nachricht retweetet, dann nicht löschen!!
                # if not (Circle_message.objects.filter(original_message = m).count() > 0):
                # antworten müssen gelöscht werden:
                # Circle_message.objects.filter(answer_to = m).delete()
                m.delete()  # TODO: muss später eingerückt werden
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


@login_required
def repost(request, message_id):
    try:
        omessage = Circle_message.objects.get(pk=message_id)
    except ObjectDoesNotExist:
        messages.error(request, "Die Original Nachricht existiert nicht")
        return HttpResponseRedirect(reverse("home"))
    if omessage.original_message:
        omessage = omessage.original_message
    if omessage.answer_to:
        messages.error(request, "Antworten koennen nicht repostet werden")
        return HttpResponseRedirect(reverse("home"))
    owncircles = Circle.objects.filter(owner=request.user)
    return render(request, "buzzit_messaging/logged_in/retweet_form.html",
                  {"circlemessage": omessage, "circles": owncircles})


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
    users = User.objects.filter(username__icontains=query).only('username')
    usernamelist = []
    for user in users[:10]:
        pic_url = reverse("profile_picture_small", args=(user.pk,))
        usernamelist.append(
            {"name": user.username, "id": user.pk, "avatar": pic_url, "type": "contact"})
    return JsonResponse({"symbol": "@", "list": usernamelist}, safe=False, )


@login_required
def search_theme_json(request, query):
    themes = Theme.objects.filter(name__icontains=query).only('name')
    if themes.count() < 1:
        theme = Theme()
        theme.name = query
        theme.pk = query
        themes = [theme]
    themenamelist = []
    for theme in themes[:10]:
        themenamelist.append({"name": theme.name, "id": theme.pk, "avatar": "", "type": "theme"})
    return JsonResponse({"symbol": "#", "list": themenamelist}, safe=False, )
    pass


@login_required
def chat_polling(request, sender_id):
    return JsonResponse({"sender_id": sender_id, "new_chat_messages": []})


@login_required
def showPostsToTheTheme(request, theme):
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
        theme = Theme.objects.get(pk=theme)
    except ObjectDoesNotExist:
        messages.error(request, "Das gewaehlte Thema existiert nicht (mehr)")
        return HttpResponseRedirect(reverse_lazy("home"))

    # get all available messages with this theme
    try:
        circle_in_which_i_am_a_member = Circle.objects.filter(
            members=request.user)  # get the circle in which i am a member
        for circle in circle_in_which_i_am_a_member:
            all_posts_which_i_can_see += (circle.messages.filter(themes=theme).all())
    except ObjectDoesNotExist:
        messages.error(request, "Du hast noch keine Kreise")
    return render(request, "buzzit_messaging/logged_in/theme_details.html", {"post_list": posts})


class PostDetailsView(ListView):
    """
    Gives the ability to view details about the circlemessage by message_id.
    :param request:
    :param message_id:
    :return:
    """
    model = Circle_message
    template_name = "buzzit_messaging/logged_in/post_details.html"
    context_object_name = "answer_list"

    def get_context_data(self, **kwargs):
        context = super(PostDetailsView, self).get_context_data(**kwargs)
        currentcirclemessageid = self.kwargs.get("slug")
        context["circlemessage"] = Circle_message.objects.get(pk=currentcirclemessageid)
        return context

    def get_queryset(self):
        currentcirclemessageid = self.kwargs.get("slug")
        return Circle_message.objects.filter(answer_to__id=currentcirclemessageid).order_by('created')

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(PostDetailsView, self).dispatch(request, *args, **kwargs)


from django.db.models import Q


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
    all_chat_messages_for_me = Directmessage.objects.filter(
        Q(receiver=request.user) | Q(creator=request.user), ~Q(creator__username="SYSTEM")).order_by("created").all()
    chats = {}
    chats["SYSTEM"] = Directmessage.objects.filter(receiver=request.user, creator__username="SYSTEM").order_by("created")
    chatsMsgCount = {}
    for cm in all_chat_messages_for_me:
        if cm.creator == request.user:
            chats[cm.receiver.username] = cm
            if not cm.read:
                if chatsMsgCount.get(cm.receiver.username):
                    chatsMsgCount[cm.receiver.username] += 1
                else:
                    chatsMsgCount[cm.receiver.username] = 1
        else:
            chats[cm.creator.username] = cm
            if not cm.read:
                if chatsMsgCount.get(cm.creator.username):
                    chatsMsgCount[cm.creator.username] += 1
                else:
                    chatsMsgCount[cm.creator.username] = 1
    active_conversation_partner = request.GET.get("active_conversation")  # string
    if active_conversation_partner:
        # client wants so see one specific chat
        conversation = Directmessage.objects.filter(
            Q(receiver=request.user, creator__username=active_conversation_partner) |
            Q(creator=request.user, receiver__username=active_conversation_partner)) \
            .order_by("-created").all()
    else:
        # no specific chat given; show notifications
        active_conversation_partner = "SYSTEM"
        conversation = Directmessage.objects.filter(creator__username="SYSTEM", receiver=request.user)
    return render(request, "buzzit_messaging/logged_in/direct_messages.html",
                  {
                      "chats": chats,
                      "chatsMsgCount": chatsMsgCount,
                      "active_conversation_partner": active_conversation_partner,
                      "conversation": conversation
                  })


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
