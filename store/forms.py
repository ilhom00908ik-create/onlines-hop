from django import forms
from django.contrib.auth.models import User
from .models import Profile, Product, Order, ReelsVideo

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['phone', 'avatar']

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'

class OrderForm(forms.ModelForm):
    first_name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'placeholder': 'Masalan: Ali'}))
    last_name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'placeholder': 'Masalan: Valiye' }))
    phone = forms.CharField(max_length=20, required=True, widget=forms.TextInput(attrs={'placeholder': '+998 90 123 45 67'}))
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 2, 'placeholder': 'Shahar, ko\'cha, uy raqami'}), required=True)

    class Meta:
        model = Order
        # Faqat foydalanuvchi to'ldiradigan maydonlarni qoldiramiz:
        fields = ['phone', 'address']

class ReelsVideoForm(forms.ModelForm):
    class Meta:
        model = ReelsVideo
        fields = '__all__'