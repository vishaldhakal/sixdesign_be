from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Website, Activity, People, Tag

@admin.register(Website)
class WebsiteAdmin(ModelAdmin):
    list_display = ['name', 'domain', 'user', 'created_at']
    search_fields = ['name', 'domain']
    readonly_fields = ['site_id', 'tracking_code']

@admin.register(Activity)
class ActivityAdmin(ModelAdmin):
    list_display = ['activity_type', 'website', 'people', 'page_title', 'occured_at']
    list_filter = ['activity_type', 'website', 'occured_at']
    search_fields = ['people__name', 'people__email', 'page_title']
    date_hierarchy = 'occured_at'

@admin.register(People)
class PeopleAdmin(ModelAdmin):
    list_display = ['name', 'email', 'phone', 'stage', 'last_activity']
    list_filter = ['stage', 'created_at']
    search_fields = ['name', 'email', 'phone']
    filter_horizontal = ['tags']

@admin.register(Tag)
class TagAdmin(ModelAdmin):
    list_display = ['name']
    search_fields = ['name']
