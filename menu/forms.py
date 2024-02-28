from django import forms 
from .models import Category, FoodItem




class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ('category_name','description')


class FoodItemsForm(forms.ModelForm):
    class Meta:
        model = FoodItem
        fields = ('food_title', 'description', 'price', 'image',)
