__author__ = 'User'
from django import template
from django.core.urlresolvers import reverse
import re
from buzzit_models.models import User, Circle_message

register = template.Library()


def messagefilter(message):
    """
    :param message:
    :return:
    """
    message_text = message.text
    # parse mentions
    for mention in message.mentions.all():
        link = reverse("view_profile", args=(mention.pk,))
        link = "<a href='%s'>@%s</a>" % (link, mention.username)
        message_text = re.sub(r"\b%s\b" % mention.username, link, message_text)
    # parse themes
    for theme in message.themes.all():
        link = reverse("search_theme", args=(theme.pk,))
        link = "<a href='%s'>#%s</a>" % (link, theme.name)
        message_text = re.sub(r"\b%s\b" % theme.name, link, message_text)
    return message_text


register.filter('messagefilter', messagefilter)


def notificationfilter(message_text):
    # [.....] <POST:123> [...]
    # => [.....] <a href="link_zum_post">Post</a>
    post_ids = re.finditer("\<POST:(?P<id>[0-9]+)\>", message_text)
    for post_id in post_ids:
        id = int(post_id.groupdict()["id"])
        try:
            id = Circle_message.objects.get(pk=id)
            link_to_post = "<a href='%s'>(link)</a>" % reverse("one_circlemessage", args=(id,))
        except Exception:
            link_to_post = "<a href='#'>(geloescht)</a>"
        message_text = re.sub("\<POST:(?P<id>[0-9]+)\>", link_to_post, message_text)

    user_ids = re.finditer("\<USER:(?P<id>[a-zA-Z0-9]+)\>", message_text)
    for user_id in user_ids:
        id = user_id.groupdict()["id"]
        try:
            id = User.objects.get(username=id)
            link_to_user = "<a href='%s'>%s</a>" % (id.username, reverse("view_profile", args=(id.pk,)))
        except Exception:
            link_to_user = "<a href='#'>(geloescht)</a>";
        message_text = re.sub("\<USER:(?P<id>[a-zA-Z0-9]+)\>", link_to_user, message_text)
    # ersetze user
    return message_text


register.filter('notificationfilter', notificationfilter)
