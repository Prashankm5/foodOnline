from django.contrib import admin

from .models import Cart, Tax

# Register your models here.
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display=('user', 'fooditem', 'quantity', 'updated_at')


@admin.register(Tax)
class TaxAdmin(admin.ModelAdmin):
    list_display=('id', 'tax_type', 'tax_percentage', 'is_active',)
