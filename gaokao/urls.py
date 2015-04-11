from django.conf.urls import patterns, include, url
from django.contrib import admin
import settings

# tastypie API urls
from tastypie.api import Api
from pi.api import *
v1_api = Api(api_name='v1')
v1_api.register(SchoolResource())

urlpatterns = patterns('',
    url(r'^api/', include(v1_api.urls)),
	url(r'^gaokao/', include ('pi.urls')),
    url(r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += patterns('',
        url(r'^__debug__/', include(debug_toolbar.urls)),
    )

    urlpatterns += patterns('django.contrib.staticfiles.views',
        url(r'^static/(?P<path>.*)$', 'serve'),
    )
