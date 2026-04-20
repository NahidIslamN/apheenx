from django.contrib import admin


from django.contrib import admin
from django.utils.html import format_html
from .models import Image, Product, Orders

@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'image_preview', 'created_at')
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 50px; height: auto;" />', obj.image.url)
        return "No Image"
    image_preview.short_description = 'Preview'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    # Columns to show in the list view
    list_display = (
        'product_name', 
        'category', 
        'price', 
        'stock_quantity', 
        'status', 
        'is_active', 
        'is_featured'
    )
    
    # Right sidebar filters
    list_filter = ('category', 'status', 'is_active', 'is_featured', 'created_at')
    
    # Search functionality
    search_fields = ('product_name', 'product_description')
    
    # Make ManyToMany easier to manage
    filter_horizontal = ('product_images',)
    
    # Organizing fields into sections
    fieldsets = (
        ('Basic Information', {
            'fields': ('product_name', 'product_description', 'category', 'status')
        }),
        ('Pricing & Stock', {
            'fields': ('price', 'discount_price', 'stock_quantity', 'sales_count')
        }),
        ('Media & Visibility', {
            'fields': ('product_images', 'is_featured', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',), # Hide by default
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Orders)
class OrdersAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'order_total', 'is_paid', 'city', 'created_at')
    
    # Filter by payment status and date
    list_filter = ('is_paid', 'created_at', 'country', 'city')
    
    # Search by user info or address
    search_fields = ('user__username', 'email', 'phone', 'city', 'postal_code')
    
    # UI helper for the ManyToMany products list
    filter_horizontal = ('products',)
    
    # View-only fields that shouldn't be edited manually
    readonly_fields = ('order_total', 'created_at', 'updated_at')

    def save_model(self, request, obj, form, change):
        """
        Ensures the total is recalculated if you save via Admin.
        """
        super().save_model(request, obj, form, change)
        obj.calculate_order_total()