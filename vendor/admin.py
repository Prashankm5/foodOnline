from django.contrib import admin
from .models import Vendor, OpeningHour

# Register your models here.
class VendorAdmin(admin.ModelAdmin):
    list_display=('id', 'user', 'vendor_name', 'is_approved', 'created_at')
    list_display_links=('user', 'vendor_name',)
    list_editable = ('is_approved',)

admin.site.register(Vendor, VendorAdmin)
@admin.register(OpeningHour)
class OpeningHourAdmin(admin.ModelAdmin):
    list_display=['vendor', 'day', 'from_hour', 'to_hour']
