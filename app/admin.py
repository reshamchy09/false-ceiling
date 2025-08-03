from django.contrib import admin
from .models import *

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price_per_sqft', 'is_active', 'created_at',]
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['is_active']

@admin.register(MyServices)
class MyServicesAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'price_per_sqft', 'is_active', 'created_at', 'is_featured',]
    list_filter = ['category', 'is_active', 'created_at','is_featured',]
    search_fields = ['title','description']
    list_editable = ['is_active','is_featured']


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'location', 'is_featured', 'completed_date']
    list_filter = ['category', 'is_featured', 'completed_date']
    search_fields = ['title', 'location']

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ['name', 'rating', 'location', 'is_approved', 'created_at']
    list_filter = ['rating', 'is_approved', 'created_at']
    actions = ['approve_testimonials']
    
    def approve_testimonials(self, request, queryset):
        queryset.update(is_approved=True)
    approve_testimonials.short_description = "Approve selected testimonials"

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'subject', 'is_responded', 'created_at']
    list_filter = ['is_responded', 'created_at']
    search_fields = ['full_name', 'email', 'subject']

@admin.register(EstimateRequest)
class EstimateRequestAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'ceiling_type', 'estimated_cost', 'created_at']
    list_filter = ['ceiling_type', 'quality', 'created_at']

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'is_published', 'created_at']
    list_filter = ['is_published', 'created_at', 'author']
    search_fields = ['title', 'content']
    prepopulated_fields = {'slug': ('title',)}

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ['question', 'category', 'order', 'is_active']
    list_filter = ['category', 'is_active']
    ordering = ['order']
