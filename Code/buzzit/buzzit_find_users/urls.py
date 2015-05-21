__author__ = 'David'

from django.conf.urls import include, url
from . import views

urlpatterns = [
    url(r'^user/(?P<username>[a-zA-Z0-9]+)/', views.find_users(), name="find_user"),
]