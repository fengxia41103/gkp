from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    # Examples:
	url(r'^gaokao/', include ('pi.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
