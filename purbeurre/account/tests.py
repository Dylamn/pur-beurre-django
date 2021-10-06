from django.test import TestCase
from django.shortcuts import reverse
from django.utils.crypto import get_random_string

from .models import User
from .forms import RegisterUserForm


def create_user_data(i=0):
    random_password = get_random_string(16)
    return {
        "username": f"user{i}",
        "email": f"user{i}@example.com",
        "first_name": f"firstname{i}",
        "last_name": f"lastname{i}",
        "password1": random_password,
        "password2": random_password,
    }


class RegisterViewTests(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        """Set up data for the whole TestCase."""
        cls.url = reverse('register')

    def test_register_template(self):
        """Test the template used for the register page."""
        response = self.client.get(self.url)

        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, template_name='account/register.html')

    def test_register_form(self):
        """Test the RegisterUserForm validation."""
        user_data = create_user_data(0)
        register_form = RegisterUserForm(user_data, initial={'is_active': True})

        self.assertTrue(register_form.is_valid())
        self.assertTrue(register_form.initial['is_active'])

    def test_register_view_success(self):
        user_data = create_user_data(1)

        response = self.client.post(self.url, data=user_data)

        # User is redirected to the homepage on success.
        self.assertRedirects(response, reverse('home:index'), status_code=301, target_status_code=200)

        self.assertTrue(User.objects.filter(email=user_data['email']).exists())
