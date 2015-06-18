__author__ = 'User'
from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^myfollowers/$', views.beingFollowedByView, name="my_followers"),
    url(r'^circle/new/$', views.CreateCircleView.as_view(), name="new_circle"),
    url(r'^circle/(?P<slug>[0-9]+)/$', views.circleDetails, name="circle_details"),
    url(r'^circle/(?P<circle_id>[0-9]+)/addusers/$', views.add_users_to_circle, name="add_users_to_circle"),
    url(r'^circle/(?P<user_id>[0-9]+)/adduser/$', views.add_user_to_circles, name="add_user_to_circles"),
    url(r'^circle/(?P<user_id>[0-9]+)/(?P<circle_id>[0-9]+)/removeuser/$', views.remove_user_from_circle, name="remove_user_from_circle"),
    url(r'^circle/(?P<slug>[0-9]+)/delete/$', views.RemoveCircleView, name="delete_circle"),
    url(r'^circles/$', views.CircleOverviewView.as_view(), name="circle_overview"),
    url(r'^follows/$', views.listfollows, name="list_follows"),
    url(r'^circlemessage/new/$', views.PostCirclemessageView.as_view(), name="new_circlemessage"),
    url(r'^circlemessage/(?P<message_id>[0-9]+)/delete/$', views.delete_circle_message, name="delete_circlemessage"),
    url(r'^follow/(?P<user_id>[0-9]+)/$', views.follow, name="follow"),
    url(r'^unfollow/(?P<user_id>[0-9]+)/$', views.unfollow, name="unfollow"),
]
