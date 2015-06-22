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
    url(r'^circlemessage/new/$', views.postCirclemessage, name="new_circlemessage"),
    url(r'^circlemessage/(?P<message_id>[0-9]+)/delete/$', views.delete_circle_message, name="delete_circlemessage"),
    url(r'^follow/(?P<user_id>[0-9]+)/$', views.follow, name="follow"),
    url(r'^unfollow/(?P<user_id>[0-9]+)/$', views.unfollow, name="unfollow"),
    # new since sprint 4
    url(r'^are_there_new_notifications/$', views.information_about_new_directmessages, name="notification_polling"),
    url(r'^circle/message/(?P<slug>[0-9]+)/$', views.one_circlemessage, name="one_circlemessage"),
    url(r'^circle/message/(?P<message_id>[0-9]+)/answer$', views.answer_to_circlemessage, name="answer_circlemessage"),
    url(r'^circle/message/(?P<message_id>[0-9]+)/repost$', views.RepostView.as_view(), name="repost_circlemessage"),
    url(r'^chat/(?P<sender_id>[0-9]+)/$', views.direct_messages_details, name="chat"),
    url(r'^chat/(?P<sender_id>[0-9]+)/poll/json$', views.chat_polling, name="chat_polling"),
    url(r'^chats/$', views.direct_messages_overview, name="all_chats"),
    url(r'^search/user/(?P<query>[a-zA-Z0-9]+)/json$', views.search_user_json, name="search_user_json"),
    url(r'^search/theme/(?P<query>[a-zA-Z0-9]+)/json$', views.search_theme_json, name="search_theme_json"),
    url(r'^search/theme/(?P<theme>[a-zA-Z0-9]+)', views.showPostsToTheTheme, name="search_theme"),
]
