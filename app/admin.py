from django.contrib import admin
from .models import *
from django.utils.html import format_html


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

@admin.register(LocationPrice)
class LocationPriceAdmin(admin.ModelAdmin):
    list_display = ("location", "additional_price", "created_at")
    search_fields = ("location",)
    ordering = ("location",)




##############################################
# ---------------- Inline for ContactServiceSelection ----------------
class ContactServiceSelectionInline(admin.TabularInline):
    model = ContactServiceSelection
    extra = 0
    readonly_fields = ('get_service_image', 'service', 'width', 'length', 'get_category')
    can_delete = False
    fields = ('get_service_image', 'service', 'width', 'length', 'get_category')

    def has_add_permission(self, request, obj=None):
        return False

    # Show service category
    def get_category(self, obj):
        return obj.service.category
    get_category.short_description = "Category"

    # Show service image
    def get_service_image(self, obj):
        if obj.service.image:
            return format_html(
                '<img src="{}" width="80" height="80" style="object-fit: cover; border-radius: 5px;" />',
                obj.service.image.url
            )
        return "-"
    get_service_image.short_description = "Image"


# ---------------- Admin for ContactSubmission ----------------
@admin.register(ContactSubmission)
class ContactSubmissionAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'phone', 'rooms', 'address', 'created_at',)
    list_filter = ('created_at',)
    search_fields = ('full_name', 'email', 'phone', 'rooms')
    readonly_fields = ('full_name', 'email', 'phone', 'address', 'rooms', 'message', 'created_at')
    inlines = [ContactServiceSelectionInline]

    # Show related services with dimensions, category, and image in list display
    def get_services(self, obj):
        services_html = ""
        for s in obj.contactserviceselection_set.all():
            try:
                width = float(s.width)
            except (ValueError, TypeError):
                width = s.width
            try:
                length = float(s.length)
            except (ValueError, TypeError):
                length = s.length

            if s.service.image:
                services_html += format_html(
                    '{} ({}x{}) - {} <br><img src="{}" width="60" height="60" style="object-fit: cover; border-radius: 5px;"/><br>',
                    s.service.title, width, length, s.service.category, s.service.image.url
                )
            else:
                services_html += format_html(
                    '{} ({}x{}) - {}<br>',
                    s.service.title, width, length, s.service.category
                )
        return format_html(services_html)

    get_services.short_description = "Services"

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return True
    





@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "post", "created_at")
    list_filter = ("created_at", "post")
    search_fields = ("name", "email", "body")
    ordering = ("-created_at",)