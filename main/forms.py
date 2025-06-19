from django import forms
from .models import *
from django.contrib.auth.hashers import make_password
from django.utils.dateparse import parse_date


class UserForm(forms.ModelForm):
    comfirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'id': 'confirm_password'}))

    class Meta:
        model = User
        fields = ('username', 'email', 'password')
        widgets = {
            'password': forms.PasswordInput(attrs={'id': 'password'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        comfirm_password = cleaned_data.get('comfirm_password')
        if password != comfirm_password:
            raise forms.ValidationError('Passwords do not match')
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.password = make_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user
    


class CustomDateField(forms.DateField):
    widget = forms.DateInput(format='%m/%d/%Y')

    def to_python(self, value):
        return parse_date(value, '%m/%d/%Y')


class UploadPostForm(forms.ModelForm):
    class Meta:
        model = Upload_post
        fields = ( 'image', 'video', 'content')

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']


class ProfileForm(forms.ModelForm):
    b_day = CustomDateField()
    class Meta:
        model = Profile
        fields = ['profile_picture', 'bio', 'b_day', 'phone_number', 'address', 'gender']



class EditUserProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'b_day', 'phone_number', 'address', 'gender']
        widgets = {
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'b_day': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
        }


class EditUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['f_name', 'm_name', 'l_name', 'email', 'username']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your username'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your email'
            }),
            'f_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your first name'
            }),
            'm_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your middle name'
            }),
            'l_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your last name'
            }),
        }

