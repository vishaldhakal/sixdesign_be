from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Expense, ExpenseCategory

@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(ModelAdmin):
    list_display = ('name',)
    search_fields = ('name', 'description')

@admin.register(Expense)
class ExpenseAdmin(ModelAdmin):
    list_display = ('title', 'amount', 'category', 'expense_date', 'created_by')
    list_filter = ('category', 'expense_date', 'created_by')
    search_fields = ('title', 'description')
    date_hierarchy = 'expense_date'
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'amount', 'category', 'expense_date')
        }),
        ('Details', {
            'fields': ('description', 'receipt')
        }),
        ('System Fields', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
