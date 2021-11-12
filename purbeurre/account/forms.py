from django.contrib.auth.forms import UserCreationForm

from .models import User


class RegisterUserForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        common_css_class = {'class': 'form-control'}  # Bootstrap 5.x class

        for field_name in self.fields:
            self.fields[field_name].widget.attrs.update(common_css_class)

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name", "password1", "password2"]
