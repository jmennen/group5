from django.conf.urls import include, url
from . import views

urlpatterns = [
    url(r'^profile/(?P<slug>[0-9]+)/$', views.view_profile, name="view_profile"),
    url(r'^profile/(?P<slug>[0-9]+)/picture/full$', views.profilepicture_full, name="profile_picture_full"),
    url(r'^profile/(?P<slug>[0-9]+)/picture/small$', views.profilepicture_small, name="profile_picture_small"),
    url(r'^updateprofile', views.EditProfileView.as_view(), name="update_profile"),
    url(r'^updateuser', views.EditUserdataView.as_view(), name="update_userdata"),
    url(r'^changepassword', views.password_change, name="change_password"),
    url(r'^changepassworddone', views.home, name="password_change_done"),
    url(r'^search/', views.UserSearchResultsView.as_view(), name="search_user"),
    url(r'^register', views.register, name="register"),
    url(r'^$', views.start, name="start"),
    url(r'^home$', views.home, name="home"),
    url(r'^impressum', views.impressum, name="impressum"),
    url(r'^accounts/login', views.start, name="login"),
    url(r'^logout', views.logout, name="logout"),
    url(r'^resetpassword', views.reset_password, name="reset_password"),
    url(r'^activeaccount/(?P<username>[a-zA-Z0-9]+)/(?P<token>[a-zA-Z0-9]+)', views.activateaccount, name="activate_account"),
]
