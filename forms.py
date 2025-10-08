from django import forms
from admin_site.models import Category, Product


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = "__all__"
        widgets = {
            "name_uz": forms.TextInput(attrs={'class': 'form-control'}),
            "name_ru": forms.TextInput(attrs={'class': 'form-control'}),
            "parent_id": forms.TextInput(attrs={'class': 'form-control'}),
        }


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = "__all__"
        widgets = {
            "name_uz": forms.TextInput(attrs={'class': 'form-control'}),
            "name_ru": forms.TextInput(attrs={'class': 'form-control'}),
            "price": forms.NumberInput(attrs={'class': 'form-control'}),
            "description_uz": forms.Textarea(attrs={'class': 'form-control'}),
            "description_ru": forms.Textarea(attrs={'class': 'form-control'}),
            "category_id": forms.Select(attrs={'class': 'form-control'}),
        }