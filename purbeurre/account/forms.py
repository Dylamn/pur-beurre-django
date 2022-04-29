from django import forms
from django.forms.utils import ErrorList
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _

from .models import User


class CustomErrorList(ErrorList):
    def __init__(self, initlist=None, error_class=None):
        if error_class is None:
            error_class = 'mb-1'

        super(CustomErrorList, self).__init__(initlist=initlist, error_class=error_class)
        

class UserUpdateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(UserUpdateForm, self).__init__(*args, **kwargs)
        self.error_class = CustomErrorList

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        error_messages = {
            'email': {
                'unique': _('Cette adresse email est déjà utilisée.')
            }
        }


class RegisterUserForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        common_css_class = {'class': 'form-control'}  # Bootstrap 5.x class

        for field_name in self.fields:
            self.fields[field_name].widget.attrs.update(common_css_class)

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name", "password1", "password2"]
