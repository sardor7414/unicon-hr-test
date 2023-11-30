from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .resources import TodoResource
from .models import Region, District, Task, Member, Todo

# Register your models here.
@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ('region', 'name', 'user')


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('id', 'district', 'full_name', 'phone', 'telegram_id', 'user')


class TodoAdmin(ImportExportModelAdmin):
    list_display = ('id', 'member', 'organization', 'task', 'get_location_link', 'photo', 'created_at')
    list_filter = ('id', 'member', 'task', 'created_at')
    resource_class = TodoResource

    def get_location_link(self, obj):
        latitude, longitude = obj.location['latitude'], obj.location['longitude']
        return f'https://www.google.com/maps/place/{latitude},{longitude}'


admin.site.register(Todo, TodoAdmin)