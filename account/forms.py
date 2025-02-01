from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from django import forms
from django.forms.widgets import PasswordInput,TextInput
from django.forms.models import ModelForm
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV2Checkbox
class CreateUserForm(UserCreationForm):
    class Meta:
        model=User
        fields=['username','email','password1','password2']
    
    Captcha=ReCaptchaField(required=True,widget=ReCaptchaV2Checkbox)

class LoginForm(AuthenticationForm):
    username=forms.CharField(widget=TextInput())
    password=forms.CharField(widget=PasswordInput())
    # captcha=ReCaptchaField(required=True, widget=ReCaptchaV2Checkbox)
    
class UpdateUserForm(ModelForm):
    class Meta:
        model=User
        fields=['username','email']