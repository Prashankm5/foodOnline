from django import forms
from .models import Vendor
# from accounts.validators import allow_only_images_validator


class VendorForm(forms.ModelForm):
    class Meta:
        model = Vendor
        fields = ['vendor_name', 'vendor_license']