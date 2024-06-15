from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Device, Room, Rental

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model=User
        fields = ['username','email','password1','password2'] 

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Username already exists.')
        return username
    
    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Email already exists.')
        return email

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Username already exists.')
        return username
    
    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Email already exists.')
        return email

class RentalForm(forms.ModelForm):
    class Meta:
        model = Rental
        fields = "__all__"

class DeviceForm(forms.ModelForm):
    class Meta:
        model = Device
        fields = "__all__"

class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = "__all__"

class UploadCSVForm(forms.Form):
    csv_file = forms.FileField()
    