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
from django.db.models import Q


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
            __send_system__message__(user_mentioned.pk, "Du wurdest in einem Post erwaehnt: <POST:%s>" % newPost.id)
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

        if ans:
            answer_to = Circle_message.objects.get(pk=ans)
            __send_system__message__(answer_to.creator.pk, "Dein Post <POST:%s> hat eine neue Antwort" % answer_to.pk)
        if rep:
            original_message = Circle_message.objects.get(pk=rep)
            __send_system__message__(original_message.creator.pk,
                                     "Dein Post <POST:%s> wurde repostet" % original_message.pk)

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
    """
    views, that manages the following process.
    so this gets called, when a logged in user want to follow the user identified by <user_id>
    :param request:
    :param user_id:
    :return:
    """
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
    __send_system__message__(follow_user.user.pk, "<USER:%s> folgt Dir jetzt" % request.user.username)
    return HttpResponseRedirect(reverse_lazy('home'))


@login_required
def unfollow(request, user_id):
    """
    views, that manages the unfollowing process.
    so this gets called, when a logged in user want to unfollow the user identified by <user_id>
    :param request:
    :param user_id:
    :return:
    """
    # TODO: exceptions fuer nicht gefundene user usw (wie follow())
    unfollow_user = Profile.objects.get(pk=user_id)
    my_profile = Profile.objects.get(pk=request.user.pk)
    # take circles of unfollowed user
    circles_of_unfollowed_user = Circle.objects.filter(owner=unfollow_user.pk, members=my_profile.pk)
    for circle in circles_of_unfollowed_user:
        circle.members.remove(my_profile.pk)
    my_profile.follows.remove(unfollow_user.pk)
    messages.success(request, "Du folgst %s nicht mehr" % unfollow_user.user.username)
    __send_system__message__(unfollow_user.user.pk, "<USER:%s> folgt Dir nicht mehr" % request.user.username)
    return HttpResponseRedirect(reverse_lazy('home'))


@login_required
def repost(request, message_id):
    """
    view, that allows reposting of a existing post, that is identified by <message_id>.
    if <message_id> cannot get verified the user is redirected and receives an error message.
    :param request:
    :param message_id:
    :return:
    """
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
    """
    view for searching available users whose usernames contain query.
    returns JSON data like
    {
        "symbol": "@",
        "list": [
                    {
                        "name": <name of matching user>,
                        "id" : <id of matching user>,
                        "avatar" : <url of small profile picture>,
                        "type" : "contact"
                    }
                }
    }
    :param request:
    :param query:
    :return:
    """
    users = User.objects.filter(username__icontains=query).only('username')
    usernamelist = []
    for user in users[:10]:
        pic_url = reverse("profile_picture_small", args=(user.pk,))
        usernamelist.append(
            {"name": user.username, "id": user.pk, "avatar": pic_url, "type": "contact"})
    return JsonResponse({"symbol": "@", "list": usernamelist}, safe=False, )


@login_required
def search_theme_json(request, query):
    """
    view for searching available themes.
    If theme is new, the new themename will be returned; so always returns something
    returns JSON data like
    {
        "symbol": "#",
        "list": [
                    {
                        "name": <name of matching theme>,
                        "id" : <id (also name) of matching theme>,
                        "avatar" : "" --- currently not used,
                        "type" : "theme"
                    }
                }
    }
    :param request:
    :param query:
    :return:
    """
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


from django.template.loader import render_to_string


@login_required
def chat_polling(request, username):
    """
    get info for UNREAD messages of the current chat and shortinfo for all other chats
    TODO on clientside: currently new conversations will not be displayed correctly
    :param request:
    :param username:
    :return: JSON data like
        {
            "username": username, --- the username of current conversation
            "new_chat_messages":    [
                                        <rendered unread direct message of current conversation>
                                    ],
            "chats":    {
                            "usernameX" :   {
                                                "text" : <text of latest unread chat message>,
                                                "count" : <count of unread messages>
                                            },
                            "usernameY" : ...
                        }
        }
    """
    new_messages = Directmessage.objects.filter(receiver=request.user, creator__username=username, read=False).order_by(
        "created").all()
    if new_messages.count() > 0:
        msg = []
        # msg holds the messages for current chat
        for m in new_messages:
            # pre render the new direct message according to its type
            if m.creator.username == "SYSTEM":
                # it is a notification
                msg.append(render_to_string("buzzit_messaging/includes/notifications/news.html", {"message": m}))
            else:
                # it is a direct message from a real user
                msg.append(render_to_string("buzzit_messaging/includes/chat/partner_chat_message.html", {"message": m}))
        new_messages.update(read=True)
    else:
        msg = []
    # look for other messages
    all_chat_messages_for_me = Directmessage.objects.filter(~Q(creator__username=username), receiver=request.user,
                                                            read=False).order_by("created").all()
    # build short info for chats, that are not the current conversation
    chats = {}
    # naive sorting
    for cm in all_chat_messages_for_me:
        if chats.get(cm.creator.username):
            chats[cm.creator.username]["text"] = cm.text
            chats[cm.creator.username]["count"] += 1
        else:
            chats[cm.creator.username] = {"text": cm.text, "count": 1}
    return JsonResponse({"username": username, "new_chat_messages": msg, "chats": chats}, safe=False)


from itertools import chain


@login_required
def showPostsToTheTheme(request, theme):
    """
    klick on theme and show all the posts,check if the theme exits
    filter message which man should see.
    returns <posts>, a list containing all posts with the theme
    :param request:
    :param theme:
    :return:
    """
    # look if the clicked theme exist, if not then redirect with an error message
    try:
        theme = Theme.objects.get(pk=theme)
    except ObjectDoesNotExist:
        messages.error(request, "Das gewaehlte Thema existiert nicht (mehr)")
        return HttpResponseRedirect(reverse_lazy("home"))

    # get all available messages with this theme
    # 1. get public messages
    # 2. get circled messages
    # 1. get the public messages with theme
    public_messages = Circle_message.objects.filter(public=True, themes=theme)
    # 2.
    # 2.1 get circles where logged user is put into
    circles_im_in = Circle.objects.filter(members=request.user)
    # 2.2 look if i am in any circle
    if circles_im_in.count() > 0:
        # 2.3 if so, get the messages from these circles with theme (also self created
        circled_messages = Circle_message.objects.filter(Q(circle__set=circles_im_in) | Q(creator=request.user),
                                                         public=False, themes=theme).distinct()
    else:
        # 2.3 if not, there are no circled messages
        circled_messages = Circle_message.objects.filter(creator=request.user,
                                                         public=False, themes=theme).distinct()
    # put all messages together and sort them by created date
    posts = sorted(list(chain(public_messages, circled_messages)), key=lambda instance: instance.created)
    return render(request, "buzzit_messaging/logged_in/theme_details.html", {"post_list": posts})


class PostDetailsView(ListView):
    """
    Gives the ability to view details about the circlemessage by message_id.
    returns an <answer_list> with all answers and the <circlemessge> queried
    :param request:
    :param message_id:
    :return:
    """
    model = Circle_message
    template_name = "buzzit_messaging/logged_in/post_details.html"
    context_object_name = "answer_list"

    def get_context_data(self, **kwargs):
        try:
            context = super(PostDetailsView, self).get_context_data(**kwargs)
        except Exception:
            messages.error(self.request, "Post existiert nicht")
            return HttpResponseRedirect(reverse_lazy("home"))
        currentcirclemessageid = self.kwargs.get("slug")
        # add <circlemessage> to the templates context
        try:
            context["circlemessage"] = Circle_message.objects.get(pk=currentcirclemessageid)
        except Exception:
            messages.error(self.request, "Post existiert nicht")
            context["answer_list"] = []
            return context
        return context

    def get_queryset(self):
        return HttpResponseRedirect(reverse_lazy("home"))
        currentcirclemessageid = self.kwargs.get("slug")
        try:
            Circle_message.objects.get(pk=currentcirclemessageid)
            return Circle_message.objects.filter(answer_to__id=currentcirclemessageid).order_by('created')
        except Exception:
            messages.error(self.request, "Post existiert nicht")
            return HttpResponseRedirect(reverse_lazy("home"))

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        try:
            return super(PostDetailsView, self).dispatch(request, *args, **kwargs)
        except Exception:
            return HttpResponseRedirect(reverse_lazy("home"))


@login_required
def direct_messages_overview(request):
    """
    Overview of all direct messages.
    Returns context:
    {
        "chats_sorted": sorted_chats, --- list with usernames of conversation partners sorted by username
        "chats": chats, --- unsorted dict with username-keys and latest message as value
        "chatsMsgCount": chatsMsgCount, --- unsorted dict with username-keys and unread messages count as value
        "active_conversation_partner": active_conversation_partner, --- username of current conversation
        "conversation": conversation, --- the chat itself with <conversationpartner>
        "system_messages": { --- shortinfo about systemmessages/notifications
            "count": sysMsgCount,  --- count of unread notifications
            "msg": sysMsg --- latest notification
        }
    }

    :param request:
    :return:
    """
    chatsMsgCount = {}  # this will hold count for unread messages with by key <username>
    # get latest notification
    sysMsg = Directmessage.objects.filter(receiver=request.user, creator__username="SYSTEM").order_by("-created")
    if sysMsg.count() > 0:
        sysMsg = sysMsg[0]
    else:
        sysMsg = []
    # get amount of unread notifications
    sysMsgCount = Directmessage.objects.filter(receiver=request.user, creator__username="SYSTEM", read=False).count()

    # receive all chatmessages for me and sort them by date created
    all_chat_messages_for_me = Directmessage.objects.filter(
        Q(receiver=request.user) | Q(creator=request.user), ~Q(creator__username="SYSTEM")).order_by("created").all()
    chats = {}
    # from these chatmessages only store the latest one and
    # count unread messages (own unread messages are ignored - they were sent by the logged in user)
    # naive sorting
    for cm in all_chat_messages_for_me:
        if cm.creator == request.user:
            chats[cm.receiver.username] = cm
        else:
            chats[cm.creator.username] = cm
            if not cm.read:
                if chatsMsgCount.get(cm.creator.username):
                    chatsMsgCount[cm.creator.username] += 1
                else:
                    chatsMsgCount[cm.creator.username] = 1
    # look if one specific conversation is requested
    active_conversation_partner = request.GET.get("active_conversation")  # string
    # if there is a conversation partner and its not SYSTEM (notifications)
    if active_conversation_partner and active_conversation_partner != "SYSTEM":
        # the client wants so see one specific chat
        # so get this specific chat
        conversation = Directmessage.objects.filter(
            Q(receiver=request.user, creator__username=active_conversation_partner) |
            Q(creator=request.user, receiver__username=active_conversation_partner)) \
            .order_by("created")
        # and look if there are any messages yes
        if conversation.count() > 0:
            # if so, thenn mark the messages from the conversation partner as read
            # (they are received right now, so the user will read them)
            conversation.filter(receiver=request.user).all().update(read=True)
            conversation = conversation.all()
        else:
            # if there are no messages we have a
            # new conversation
            conversation = []
            dummy_msg = Directmessage()
            # so we create a dummy message, that will not be saved, but allows easy use of template
            try:
                dummy_msg.receiver = User.objects.get(username=active_conversation_partner)
            except ObjectDoesNotExist:
                messages.error("Der Benutzer existiert nicht")
                return HttpResponseRedirect(reverse("home"))
            dummy_msg.text = "NEU"
            chats[active_conversation_partner] = dummy_msg
    else:
        # no specific chat given; show notifications
        # so set the conversationpartner to SYSTEM (notifications)
        active_conversation_partner = "SYSTEM"
        # and get the notifications
        conversation = Directmessage.objects.filter(creator__username="SYSTEM", receiver=request.user).order_by(
            "created")
        # and mark them as read
        conversation.update(read=True)
    # key the usernames of all chats and sort them
    sorted_chats = list(chats)
    sorted_chats.sort()
    return render(request, "buzzit_messaging/logged_in/direct_messages.html",
                  {
                      "chats_sorted": sorted_chats,
                      "chats": chats,
                      "chatsMsgCount": chatsMsgCount,
                      "active_conversation_partner": active_conversation_partner,
                      "conversation": conversation,
                      "system_messages": {"count": sysMsgCount, "msg": sysMsg}
                  })


@login_required
def direct_messages_details(request, sender_id):
    """
    method to accept new directmessage.
    accepts only post request.
    :param request:
    :return:
    """
    if request.method == "POST":
        # look for posted text
        message_content = request.POST.get("text", False)
        if (not message_content) or len(message_content) < 1:
            # if there is no text or the text is too short redirect and show error
            messages.error(request, "Kein Text angegeben")
            return HttpResponseRedirect(reverse("home"))
        # create a new direct message and fill in data, then save it, if successful
        message_var = Directmessage()
        message_var.creator = request.user
        message_var.created = datetime.now()
        message_var.text = message_content
        try:
            message_var.receiver = User.objects.get(username=sender_id)
        except ObjectDoesNotExist:
            messages.error(request, "Den Empfaenger gibt es nicht")
            return HttpResponseRedirect(reverse("home"))
        message_var.save()
        return HttpResponseRedirect("%s?active_conversation=%s" % (reverse("all_chats"), message_var.receiver.username))


def __send_system__message__(receiver, message, level="info"):
    """
    convenience method for sending system messages/notifications
    :param receiver: the id of the receiver
    :param message: the message content
    :param level: the level, currently supported are one of: info, news, danger
    :return:
    """
    system_user = User.objects.get(username="SYSTEM")
    try:
        receiver = User.objects.get(pk=receiver)
    except ObjectDoesNotExist:
        # this should not happen, as we are sending notifications only after successful operations,
        # so the user was found before, but not yet.
        # seems to be an internal error or the user just deleted his account
        # TODO log internen fehler
        return
    sysMsg = Directmessage(creator=system_user, created=datetime.now(), receiver=receiver)
    level_msgs = {
        "info": "I%s",
        "news": "N%s",
        "danger": "D%s"
    }
    try:
        sysMsg.text = level_msgs[level] % message
    except KeyError:
        sysMsg.text = level_msgs["info"] % message
    sysMsg.save()
