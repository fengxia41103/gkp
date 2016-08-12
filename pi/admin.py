from django.contrib import admin
from pi.models import *

# Register your models here.


class MySchoolAdmin(admin.ModelAdmin):
    list_filter = ['name']
    list_display = ('name', 'city', 'province')
admin.site.register(MySchool, MySchoolAdmin)


class MyTrainStopAdmin(admin.ModelAdmin):
    list_filter = ['category']
    list_display = ('stop_name', 'stop_index', 'train_id')
admin.site.register(MyTrainStop, MyTrainStopAdmin)


class MyCityAdmin(admin.ModelAdmin):
    list_filter = ['province']
    list_display = ('city', 'province')
admin.site.register(MyCity, MyCityAdmin)

admin.site.register(MyMajor)
