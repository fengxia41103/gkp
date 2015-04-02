from django.conf.urls import patterns, url
from django.conf.urls import url
from pi import views
from django.views.generic.edit import CreateView
from django.contrib.auth.forms import UserCreationForm
import django.contrib.auth.views as AuthViews
from django.views.decorators.csrf import ensure_csrf_cookie
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = patterns(
		'',
		url(r'^$', views.HomeView.as_view(), name='home'),
		url(r'login/$', views.LoginView.as_view(),name='login'),
		url(r'logout/$', views.LogoutView.as_view(), name='logout'),
		url(r'^register/$', views.UserRegisterView.as_view(), name='user_register'),

		# user related
		url(r'^user/profile/$', views.UserProfileView.as_view(), name='user_profile'),
		url(r'^user/bookmark/$', views.UserBookmark.as_view(), name='user_bookmark'),
		url(r'^user/tags/$', views.UserTags.as_view(), name='user_tags'),

		# file import/export
		url(r'^import/admission/school/$',views.import_admission_by_school, name='import_admission_school'),
		url(r'^import/admission/major/$',views.import_admission_by_major, name='import_admission_major'),

		# admission scores by school and by major
		url(r'^admission/school/$', views.MyAdmissionBySchoolList.as_view(), name='admission_school_list'),
		url(r'^admission/school/add/$', views.MyAdmissionBySchoolAdd.as_view(), name='admission_school_add'),
		url(r'^admission/school/(?P<pk>\d+)/edit/$', views.MyAdmissionBySchoolEdit.as_view(), name='admission_school_edit'),
		url(r'^admission/school/(?P<pk>\d+)/delete/$', views.MyAdmissionBySchoolDelete.as_view(), name='admission_school_delete'),

		url(r'^admission/major/$', views.MyAdmissionByMajorList.as_view(), name='admission_major_list'),
		url(r'^admission/major/add/$', views.MyAdmissionByMajorAdd.as_view(), name='admission_major_add'),
		url(r'^admission/major/(?P<pk>\d+)/edit/$', views.MyAdmissionByMajorEdit.as_view(), name='admission_major_edit'),
		url(r'^admission/major/(?P<pk>\d+)/delete/$', views.MyAdmissionByMajorDelete.as_view(), name='admission_major_delete'),

		# major
		url(r'^major/$', views.MyMajorList.as_view(), name='major_list'),
		url(r'^major/add/$', views.MyMajorAdd.as_view(), name='major_add'),
		url(r'^major/(?P<pk>\d+)/edit/$', views.MyMajorEdit.as_view(), name='major_edit'),
		url(r'^major/(?P<pk>\d+)/delete/$', views.MyMajorDelete.as_view(), name='major_delete'),
		url(r'^major/(?P<pk>\d+)/detail/$', views.MyMajorDetail.as_view(), name='major_detail'),			
		url(r'^major/school/(?P<school_pk>\d+)/(?P<major_pk>\d+)/$', views.MyMajorSchoolDetail.as_view(), name='major_school_detail'),			
		url(r'^major/related/schools/$', ensure_csrf_cookie(views.MyMajorRelatedSchools.as_view()), name='major_related_schools'),		


		# school
		url(r'^school/$', views.MySchoolList.as_view(), name='school_list'),
		url(r'^school/add/$', views.MySchoolAdd.as_view(), name='school_add'),
		url(r'^school/(?P<pk>\d+)/edit/$', views.MySchoolEdit.as_view(), name='school_edit'),
		url(r'^school/(?P<pk>\d+)/delete/$', views.MySchoolDelete.as_view(), name='school_delete'),
		url(r'^school/(?P<pk>\d+)/detail/$', views.MySchoolDetail.as_view(), name='school_detail'),
		url(r'^school/map/filter/', ensure_csrf_cookie(views.MySchoolMapFilter.as_view()),name='school_map_filter'),
		url(r'^school/map/detail/', ensure_csrf_cookie(views.MySchoolMapDetail.as_view()),name='school_map_detail'),
		url(r'^school/map/info/', ensure_csrf_cookie(views.MySchoolMapInfo.as_view()),name='school_map_info'),
		url(r'^school/e/map/filter/$', views.MySchoolEchartMapFilter.as_view(),name='school_echart_map_filter'),
		url(r'^school/rank/(?P<rank>\d+)/$', views.MySchoolRank.as_view(), name='school_rank'),
		url(r'^school/majors/filter/tags/$', ensure_csrf_cookie(views.MySchoolMajorsFilterByTags.as_view()), name='school_majors_filter_by_tags'),

		# analysis
		url(r'^analysis/school/summary/ajax/$', views.AnalysisSchoolSummaryAJAX.as_view(), name='analysis_school_summary_ajax'),
		url(r'^analysis/school/detail/ajax/$', views.AnalysisSchoolDetailAJAX.as_view(), name='analysis_school_detail_ajax'),		
		url(r'^analysis/school/province/(?P<pk>\d+)/$', views.AnalysisSchoolByProvince.as_view(), name='analysis_school_by_province'),
		url(r'^analysis/school/city/(?P<pk>\d+)/$', views.AnalysisSchoolByCity.as_view(), name='analysis_school_by_city'),

		# 3rd party data stream integration, all AJAX!
		url(r'^baidu/tieba/ajax/$', ensure_csrf_cookie(views.IntegrationBaiduTiebaAJAX.as_view()), name='integration_baidu_tieba_ajax'),

	)+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
