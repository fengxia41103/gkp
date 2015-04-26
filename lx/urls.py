from django.conf.urls import patterns, url
from django.conf.urls import url
from lx import views
from django.views.generic.edit import CreateView
from django.contrib.auth.forms import UserCreationForm
import django.contrib.auth.views as AuthViews
from django.views.decorators.csrf import ensure_csrf_cookie
from django.conf import settings
from django.conf.urls.static import static
from django.views.decorators.cache import cache_page

urlpatterns = patterns(
	'',
	url(r'^$', views.HomeView.as_view(), name='home'),
	url(r'login/$', views.LoginView.as_view(),name='login'),
	url(r'logout/$', views.LogoutView.as_view(), name='logout'),
	url(r'^register/$', views.UserRegisterView.as_view(), name='user_register'),

	# MySEVIS
	url(r'^sevis/$', views.MySEVISList.as_view(), name='sevis_list'),
	url(r'^sevis/(?P<pk>\d+)/edit/$', views.MySEVISEdit.as_view(), name='sevis_edit'),
	url(r'^sevis/(?P<pk>\d+)/detail/$', views.MySEVISDetail.as_view(), name='sevis_detail'),

	# MyZip
	url(r'^zip/$', views.MyZipList.as_view(), name='zip_list'),
)+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
