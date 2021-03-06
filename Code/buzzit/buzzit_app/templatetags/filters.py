__author__ = 'User'
from django import template
from buzzit_models.models import Profile

register = template.Library()

def beautifulNone(val):
    """
    If the filtered object is equal to None "-nicht angegeben-" is returned.
    Else the object.
    :param val:
    :return:
    """
    if val == None or val == "":
        return "-nicht angegeben-"
    return val

register.filter('beautifulNone', beautifulNone)

def emptyNone(val):
    """
    If the filtered object is equal to None, an empty string is returned.
    :param val:
    :return:
    """
    if val == None:
        return ""
    return val

register.filter('emptyNone', emptyNone)

def addcssclass(input, cssclass):
    """
    Add the CSS class <cssclass> to the input FormField.
    :param input:
    :param cssclass:
    :return:
    """
    return input.as_widget(attrs={'class': cssclass})

register.filter('addcssclass', addcssclass)

# TODO:
def iAmFollowing(otherprofile, myprofile):
    return myprofile.follows.all().filter(pk=otherprofile)

register.filter('i_am_following', iAmFollowing)

def keyvalue(dict, key):
    try:
        return dict[key]
    except KeyError:
        return ''

register.filter('keyval', keyvalue)

def objectvalue(obj, attr):
    try:
        return getattr(obj,attr)
    except Exception:
        return ""

register.filter('objval', objectvalue)

def startswith(val, char):
    return val[0] == char

register.filter('startswith', startswith)

def withoutFirstChar(val):
    return val[1:]

register.filter('withoutFirstChar', withoutFirstChar)