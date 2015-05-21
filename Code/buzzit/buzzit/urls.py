from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    # Examples:
    # url(r'^$', 'buzzit.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^profile/', include("buzzit_user_profile.urls")),
    url(r'^find/', include("buzzit_find_users.urls")),
]
