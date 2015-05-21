__author__ = 'David'

from django.conf.urls import include, url
from . import views

urlpatterns = [
    url(r'^get/(?P<username>[a-zA-Z0-9]+)/', views.get_profile_info, name="get_profile"),
    url(r'^update/', views.update_profile_info, name="update_profile")
]