from django.contrib import admin

# Register your models here.
from lx.models import *

# Register your models here.
class MySEVISSchoolAdmin(admin.ModelAdmin):
	list_filter=['physical_zip__state']
	list_display=('name','campus_id','f_1','m_1','physical_address','physical_zip','sevis_physical','mailing_address','mailing_zip')
admin.site.register(MySEVISSchool,MySEVISSchoolAdmin)
