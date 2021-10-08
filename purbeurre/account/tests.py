import time

from django.test import TestCase, LiveServerTestCase
from django.shortcuts import reverse
from django.utils.crypto import get_random_string

from .models import User
from .forms import RegisterUserForm

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions


def create_user_data(i=0):
    """Generate simple user data for filling the registration form."""
    random_password = get_random_string(16)

    return {
        "username": f"user{i}",
        "email": f"user{i}@example.com",
        "first_name": f"firstname{i}",
        "last_name": f"lastname{i}",
        "password1": random_password,
        "password2": random_password,
    }


def default_chrome_options():
    chrome_options = Options()
    chrome_options.headless = True  # Run Chrome browser in a headless environment (without visible UI)
    chrome_options.add_argument("--no-sandbox")  # bypass OS security model
    chrome_options.add_argument("--disable-dev-shm-usage")  # overcome limited resource problems
    chrome_options.add_argument("--window-size=1920,1080")

    return chrome_options


class RegisterViewTests(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        """Set up data for the whole TestCase."""
        cls.register_url = reverse('register')

    def test_register_template(self):
        """Test the template used for the register page."""
        response = self.client.get(self.register_url)

        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, template_name='account/register.html')

    def test_register_form(self):
        """Test the RegisterUserForm validation."""
        user_data = create_user_data(0)
        register_form = RegisterUserForm(user_data, initial={'is_active': True})

        self.assertTrue(register_form.is_valid())
        self.assertTrue(register_form.initial['is_active'])

    def test_register_view_success(self):
        """Test that the POST method is correctly handled and works."""
        user_data = create_user_data(1)

        response = self.client.post(self.register_url, data=user_data)

        # User is redirected to the homepage on success.
        self.assertRedirects(response, reverse('home:index'), status_code=301, target_status_code=200)

        self.assertTrue(User.objects.filter(email=user_data['email']).exists())


class RegisterPageTests(LiveServerTestCase):
    def test_register_page_success(self):
        user_data = create_user_data(999)

        with webdriver.Chrome(chrome_options=default_chrome_options()) as driver:
            wait = WebDriverWait(driver, timeout=5)
            driver.get(f'{self.live_server_url}/accounts/register')

            self.assertTrue("S'enregistrer" in driver.page_source)

            # Get the form elements
            username_field = driver.find_element_by_id('id_username')
            email_field = driver.find_element_by_id('id_email')
            firstname_field = driver.find_element_by_id('id_first_name')
            lastname_field = driver.find_element_by_id('id_last_name')
            password1_field = driver.find_element_by_id('id_password1')
            password2_field = driver.find_element_by_id('id_password2')
            submit_button = driver.find_element_by_id('sign_up')

            # Fill the fields with value
            username_field.send_keys(user_data['username'])
            email_field.send_keys(user_data['email'])
            firstname_field.send_keys(user_data['first_name'])
            lastname_field.send_keys(user_data['last_name'])
            password1_field.send_keys(user_data['password1'])
            password2_field.send_keys(user_data['password2'])

            submit_button.send_keys(Keys.ENTER)

            wait.until(
                expected_conditions.url_to_be(self.live_server_url)
            )
            self.assertTrue(User.objects.filter(email=user_data['email']).exists())
