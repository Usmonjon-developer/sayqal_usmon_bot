from django import forms
from .models import Category, Product, User, Suggestion


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = "__all__"
        widgets = {
            "name_uz": forms.TextInput(attrs={'class': 'form-control'}),
            "name_ru": forms.TextInput(attrs={'class': 'form-control'}),
            "name_en": forms.TextInput(attrs={'class': 'form-control'}),
            "parent": forms.Select(attrs={'class': 'form-control'}),
        }


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = "__all__"
        widgets = {
            "name_uz": forms.TextInput(attrs={'class': 'form-control'}),
            "name_ru": forms.TextInput(attrs={'class': 'form-control'}),
            "name_en": forms.TextInput(attrs={'class': 'form-control'}),
            "price": forms.NumberInput(attrs={'class': 'form-control'}),
            "description_uz": forms.Textarea(attrs={'class': 'form-control'}),
            "description_en": forms.Textarea(attrs={'class': 'form-control'}),
            "description_ru": forms.Textarea(attrs={'class': 'form-control'}),
            "category": forms.Select(attrs={'class': 'form-control'}),
            "image": forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = "__all__"
        widgets = {
            "first_name": forms.TextInput(attrs={'class': 'form-control'}),
            "phone_number": forms.TextInput(attrs={'class': 'form-control'}),
            "lang_id": forms.TextInput(attrs={'class': 'form-control'}),
            "chat_id": forms.TextInput(attrs={'class': 'form-control'}),
        }

class SuggestionForm(forms.ModelForm):
    class Meta:
        model = Suggestion
        fields = ["chat_id", "message"]
        widgets = {
            "chat_id": forms.Select(attrs={'class': 'form-control'}),
            "message": forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }