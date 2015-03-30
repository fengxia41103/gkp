from django.contrib import admin
from pi.models import *

# Register your models here.
class MySchoolAdmin(admin.ModelAdmin):
	list_filter=['name']
	list_display=('name','city','province')

admin.site.register(MySchool,MySchoolAdmin)


admin.site.register(MyMajor)