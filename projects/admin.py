from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Project, Agenda, Client

@admin.register(Client)
class ClientAdmin(ModelAdmin):
    list_display = ('name', 'email', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'email', 'notes')
    date_hierarchy = 'created_at'

@admin.register(Project)
class ProjectAdmin(ModelAdmin):
    list_display = ('title', 'project_type', 'client', 'status', 'start_date', 'end_date', 'created_by')
    list_filter = ('status', 'project_type', 'client', 'created_by', 'start_date', 'end_date')
    search_fields = ('title', 'description', 'client__name')
    date_hierarchy = 'created_at'

@admin.register(Agenda)
class AgendaAdmin(ModelAdmin):
    list_display = ('title', 'project', 'assigned_to', 'deadline', 'priority', 'status')
    list_filter = ('status', 'priority', 'deadline', 'created_at')
    search_fields = ('title', 'description', 'project__title')
    date_hierarchy = 'deadline'
