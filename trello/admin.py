from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .resources import TodoResource
from .models import Region, District, Task, Member, Todo

# Register your models here.
@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    fields = ('id', 'name')

@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ('region', 'name', 'user')

    def has_change_permission(self, request, obj=None):
        if obj is not None and obj.user != request.user:
            return False
        return True

    def has_delete_permission(self, request, obj=None):
        if obj is not None and obj.user != request.user:
            return False
        return True
    def save_model(self, request, obj, form, change):
        obj.user = request.user
        super().save_model(self, request, obj, form, change)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('id', 'district', 'full_name', 'phone', 'telegram_id', 'user')

    def has_change_permission(self, request, obj=None):
        if obj is not None and obj.user != request.user:
            return False
        return True

    def has_delete_permission(self, request, obj=None):
        if obj is not None and obj.user != request.user:
            return False
        return True
    def save_model(self, request, obj, form, change):
        obj.user = request.user
        super().save_model(self, request, obj, form, change)


class TodoAdmin(ImportExportModelAdmin):
    list_display = ('id', 'member', 'organization', 'task', 'get_location_link', 'photo', 'created_at')
    list_filter = ('id', 'member', 'task', 'created_at')
    resource_class = TodoResource

    def get_location_link(self, obj):
        latitude, longitude = obj.location['latitude'], obj.location['longitude']
        return f'https://www.google.com/maps/place/{latitude},{longitude}'


admin.site.register(Todo, TodoAdmin)