__author__ = 'User'
from django import template
from django.core.urlresolvers import reverse
import re

register = template.Library()

def messagefilter(message):
    """
    :param message:
    :return:
    """
    message_text = message.text
    #parse mentions
    for mention in message.mentions.all():
        link = reverse("view_profile", args=(mention.pk,))
        link = "<a href='%s'>%s</a>" % (link, mention.username)
        message_text = re.sub(r"\b%s\b" % mention.username, link, message_text)
    #parse themes
    for theme in message.themes.all():
        link = reverse("search_theme", args=(theme.pk,))
        link = "<a href='%s'>%s</a>" % (link, theme.name)
        message_text = re.sub(r"\b%s\b" % theme.name, link, message_text)
    return message_text

register.filter('messagefilter', messagefilter)