from django.contrib import admin
from django.db.models import Model
from .models import UnsubscribeEmails
from unfold.admin import ModelAdmin

# Register your models here.

@admin.register(UnsubscribeEmails)
class UnsubscribeEmailsAdmin(ModelAdmin):
    list_display = ('email', 'reason', 'created_at')
    search_fields = ('email', 'reason')
    list_filter = ('created_at',)
