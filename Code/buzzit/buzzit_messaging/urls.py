__author__ = 'User'
from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^myfollowers/$', views.BeingFollowedByView.as_view(), name="my_followers"),
    url(r'^circle/new/$', views.CreateCircleView.as_view(), name="new_circle"),
    url(r'^circle/(?P<slug>[0-9]+)/$', views.CircleDetailsView.as_view(), name="circle_details"),
    url(r'^circle/(?P<slug>[0-9]+)/delete/$', views.CircleDetailsView.as_view(), name="delete_circle"),
    url(r'^circles/$', views.CircleOverviewView.as_view(), name="circle_overview"),
    url(r'^follows/$', views.listfollows, name="list_follows"),
    url(r'^circlemessage/new/$', views.PostCirclemessageView.as_view(), name="new_circlemessage"),
    url(r'^circlemessage/(?P<slug>[0-9]+)/delete/$', views.DeleteCirclemessageView.as_view(), name="delete_circlemessage"),
    url(r'^follow/(?P<user_id>[0-9]+)/$', views.follow, name="follow"),
    url(r'^unfollow/(?P<user_id>[0-9]+)/$', views.unfollow, name="unfollow"),
]
