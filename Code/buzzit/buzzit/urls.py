from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include("buzzit_app.urls")),
    url(r'^messaging/', include("buzzit_messaging.urls")),
	url(r'^admincontrol/', include("buzzit_admin.urls")),
]
