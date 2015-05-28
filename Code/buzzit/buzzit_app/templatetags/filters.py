__author__ = 'User'
from django import template

register = template.Library()

def beautifulNone(val):
    if val == None or val == "":
        return "-nicht angegeben-"
    return val

register.filter('beautifulNone', beautifulNone)

def emptyNone(val):
    if val == None:
        return ""
    return val

register.filter('emptyNone', emptyNone)

def addcssclass(input, cssclass):
    return input.as_widget(attrs={'class': cssclass})

register.filter('addcssclass', addcssclass)