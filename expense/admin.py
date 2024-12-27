from django.contrib import admin
from .models import Expense, ExpenseCategory, ExpenseAuditLog
from django.utils.html import format_html
from unfold.admin import ModelAdmin

@admin.register(ExpenseAuditLog)
class ExpenseAuditLogAdmin(ModelAdmin):
    list_display = ['expense_title', 'user', 'action', 'timestamp', 'ip_address']
    list_filter = ['action', 'timestamp', 'user']
    search_fields = ['expense_title', 'user__email']
    readonly_fields = ['expense_id', 'expense_title', 'user', 'action', 'changes', 'timestamp', 'ip_address']
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False

@admin.register(Expense)
class ExpenseAdmin(ModelAdmin):
    list_display = ['title', 'amount', 'category', 'expense_date', 'created_by']
    list_filter = ['category', 'expense_date', 'created_by']
    search_fields = ['title', 'description']
    readonly_fields = ['created_by', 'created_at', 'updated_at']
    
    def save_model(self, request, obj, form, change):
        if not change:  # If creating new object
            obj.created_by = request.user
        obj.save()

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            return qs.filter(created_by=request.user)
        return qs

@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']
