from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include("buzzit_app.urls")),
    url(r'^messaging/', include("buzzit_messaging.urls")),
]
