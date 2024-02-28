from django.contrib import admin
from .models import Category, FoodItem
from django.contrib.auth.admin import UserAdmin

# Register your models here.
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('category_name',)}
    list_display = ('vendor', 'category_name', 'description', 'created_at', 'updated_at')
    search_fields = ('vendor__vendor_name', 'category_name')


@admin.register(FoodItem)
class FoodItemAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('food_title',)}
    list_display = ('vendor', 'category', 'food_title', 'description', 'price', 'is_available')
    search_fields = ('food_title', 'category__category_name')


