from django.conf.urls import include, url
from . import views

urlpatterns = [
    url(r'^admin/$', views.adminFrontPage, name="admin_frontpage"),
    url(r'^reportdetails/(?P<user_id>[0-9]+)/user$', views.UserReportDetailsView.as_view(), name="user_report_details"),
    url(r'^reportdetails/(?P<slug>[0-9]+)/message$', views.MessageReportDetailsView.as_view(), name="message_report_details"),
    url(r'^reportdetails/(?P<report_id>[0-9]+)/message/delete$', views.delete_reported_post, name="delete_reported_post"),
    url(r'^admins/$', views.AdminOverviewView, name="admins_overview"),
    url(r'^admins/(?P<user_id>[0-9]+)/addadmin/$', views.promote_user_to_admin, name="promote_user"),
    url(r'^admins/(?P<user_id>[0-9]+)/removeadmin/$', views.demote_admin_to_user, name="demote_admin"),
    url(r'^report/(?P<user_id>[0-9]+)/user/', views.report_user, name="report_user"),
    url(r'^report/(?P<user_id>[0-9]+)/user/save$', views.UserReportDetailsView.as_view(), name="save_report_user"),
    url(r'^report/(?P<message_id>[0-9]+)/message$', views.report_message, name="report_message"),
    url(r'^ban/(?P<user_id>[0-9]+)/$', views.ban_user, name="ban_user")
    ]
