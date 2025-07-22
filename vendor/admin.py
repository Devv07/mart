from django.contrib import admin
from .models import Product, Category, Order

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'vendor', 'category', 'price', 'stock', 'is_new']
    list_filter = ['category', 'is_new', 'vendor']
    search_fields = ['name', 'description']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'product', 'quantity', 'total_amount', 'status', 'created_at']
    list_filter = ['status', 'created_at', 'product__vendor']
    search_fields = ['user__email', 'product__name']