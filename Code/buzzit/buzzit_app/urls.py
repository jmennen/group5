from django.conf.urls import include, url
from . import views

urlpatterns = [
    url(r'^profile/(?P<slug>[0-9]+)/$', views.ProfileView.as_view(), name="view_profile"),
    url(r'^profile/(?P<slug>[0-9]+)/picture/full$', views.profilepicture_full, name="profile_picture_full"),
    url(r'^profile/(?P<slug>[0-9]+)/picture/small$', views.profilepicture_small, name="profile_picture_small"),
    url(r'^updateprofile', views.EditProfileView.as_view(), name="update_profile"),
    url(r'^updateuser', views.EditUserdataView.as_view(), name="update_userdata"),
    url(r'^search/(?P<slug>[a-zA-Z0-9]+)/', views.UserSearchResultsView.as_view(), name="search_user"),
    url(r'^register', views.register, name="register"),
    url(r'^$', views.start, name="start"),
    url(r'^home$', views.home, name="home"),
    url(r'^accounts/login', views.start, name="login"),
    url(r'^logout', views.logout, name="logout"),
]
