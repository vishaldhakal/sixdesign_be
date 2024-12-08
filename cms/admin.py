from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Category, Tag, Service, Portfolio, Blog, Testimonial
from tinymce.widgets import TinyMCE
from django.db import models
@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(Tag)
class TagAdmin(ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(Service)
class ServiceAdmin(ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(Portfolio)
class PortfolioAdmin(ModelAdmin):
    list_display = ['name', 'category', 'link']
    list_filter = ['category', 'tags', 'services']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ['tags', 'services']

@admin.register(Blog)
class BlogAdmin(ModelAdmin):
    list_display = ['title', 'category', 'created_at', 'updated_at']
    list_filter = ['category', 'tags', 'created_at']
    search_fields = ['title', 'content', 'short_description']
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ['tags']
    date_hierarchy = 'created_at'

@admin.register(Testimonial)
class TestimonialAdmin(ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name', 'description']
    date_hierarchy = 'created_at'
    formfield_overrides = {
        models.TextField: {'widget': TinyMCE()},
    }