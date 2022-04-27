from django.test import TestCase, LiveServerTestCase, tag
from django.utils.crypto import get_random_string
from django.shortcuts import reverse
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

from account.models import User
from account.forms import RegisterUserForm
from account.tests.factories import UserFactory


def create_user_data(i: int = 0) -> dict:
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


class RegisterViewTests(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        """Set up data for the whole TestCase."""
        cls.register_url = reverse('register')

    def test_register_template(self) -> None:
        """Test the template used for the register page."""
        response = self.client.get(self.register_url)

        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, template_name='account/register.html')

    def test_register_form_is_valid(self) -> None:
        """Test the RegisterUserForm validation."""
        user_data = create_user_data(0)
        register_form = RegisterUserForm(user_data, initial={'is_active': True})

        self.assertTrue(register_form.is_valid())
        self.assertTrue(register_form.initial['is_active'])

    def test_register_form_is_invalid(self):
        user_data = create_user_data(0)
        user_data['email'] = "abc.d.xyz"
        register_form = RegisterUserForm(user_data)

        self.assertFalse(register_form.is_valid())
        self.assertEqual(1, len(register_form.errors))

    def test_register_view_success(self) -> None:
        """Test that the POST method is correctly handled and works."""
        user_data = create_user_data(1)

        response = self.client.post(self.register_url, data=user_data)

        # User is redirected to the homepage on success.
        self.assertRedirects(response, reverse('home:index'), status_code=302, target_status_code=200)
        self.assertTrue(User.objects.filter(email=user_data['email']).exists())

    def test_register_view_redirect_when_authenticated(self):
        user = UserFactory()
        self.client.force_login(user)

        response = self.client.get(self.register_url)

        self.assertRedirects(response, expected_url=reverse('home:index'))

    def test_register_view_failure(self) -> None:
        """Test that the user email must be unique at sign up."""
        user_data = create_user_data(2)

        response_success = self.client.post(self.register_url, data=user_data)
        self.assertRedirects(response_success, reverse('home:index'), status_code=302, target_status_code=200)

        # When a registration request is successful, behind the scene, the user is automatically logged in.
        # So, we must logout in order to clear the client session which keep the user authenticated.
        # If we don't logout, the following request will results as an HTTP redirect response
        # because an authenticated user requested the register page.
        self.client.logout()

        response_failure = self.client.post(self.register_url, data=user_data)
        self.assertEqual(400, response_failure.status_code)


class LoginViewTests(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.login_url = reverse('login')

    def test_login_template(self):
        response = self.client.get(self.login_url)

        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, template_name='registration/login.html')

    def test_login_with_valid_credentials(self):
        password = "password_login_success"
        user = UserFactory(password=password)

        credentials = {
            "username": user.email,
            "password": password,
        }

        response = self.client.post(self.login_url, data=credentials)

        self.assertRedirects(response, reverse('home:index'))

    def test_login_with_invalid_credentials(self):
        credentials = {
            "username": "user@example.com",
            "password": "password_login_failed",
        }
        response = self.client.post(self.login_url, data=credentials)

        self.assertEqual(200, response.status_code)
        self.assertContains(response, "Adresse email ou mot de passe incorrect.")


class ProfileViewTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super(ProfileViewTests, cls).setUpClass()
        cls.url = reverse('profile')

    def setUp(self) -> None:
        self.user = UserFactory(password='password123')
        self.client.force_login(self.user)

    def test_profile_template(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='account/profile.html')

    def test_profile_page_content(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)

        self.assertContains(response, self.user.last_name)
        self.assertContains(response, self.user.first_name)
        self.assertContains(response, self.user.email)


@tag('selenium')
class SeleniumTests(LiveServerTestCase):
    # Each user of the fixture `users.json` has a password with "password" as value
    fixtures = ['users.json']

    def setUp(self) -> None:
        """Hook method for setting up the test fixture before exercising it."""
        chrome_options = Options()
        chrome_options.headless = True  # Run Chrome browser in a headless environment (without visible UI)
        chrome_options.add_argument("--no-sandbox")  # bypass OS security model
        chrome_options.add_argument("--disable-dev-shm-usage")  # overcome limited resource problems

        self.browser = webdriver.Chrome(chrome_options=chrome_options)
        self.wait = WebDriverWait(self.browser, timeout=5)

    def test_register_page_success(self) -> None:
        """Test the register page form with selenium."""
        user_data = create_user_data(999)
        url = self.live_server_url + reverse('register')

        self.browser.get(url)

        self.assertIn("S'enregistrer", self.browser.page_source)

        # Get the form elements
        username_field = self.browser.find_element_by_id('id_username')
        email_field = self.browser.find_element_by_id('id_email')
        firstname_field = self.browser.find_element_by_id('id_first_name')
        lastname_field = self.browser.find_element_by_id('id_last_name')
        password1_field = self.browser.find_element_by_id('id_password1')
        password2_field = self.browser.find_element_by_id('id_password2')
        submit_button = self.browser.find_element_by_id('sign_up')

        # Fill the fields with value
        username_field.send_keys(user_data['username'])
        email_field.send_keys(user_data['email'])
        firstname_field.send_keys(user_data['first_name'])
        lastname_field.send_keys(user_data['last_name'])
        password1_field.send_keys(user_data['password1'])
        password2_field.send_keys(user_data['password2'])

        submit_button.send_keys(Keys.ENTER)

        self.wait.until(
            expected_conditions.url_changes(url)
        )

        # Check if the user has been created
        self.assertTrue(User.objects.filter(email=user_data['email']).exists())

    def test_login_page_success(self):
        """Test the login page form with selenium"""
        password = "password"
        email = 'macgyver@example.com'

        url = str(self.live_server_url + reverse('login'))

        self.browser.get(url)

        email_field = self.browser.find_element_by_id('username')
        password_field = self.browser.find_element_by_id('password')
        submit_button = self.browser.find_element_by_id('login_button')

        email_field.send_keys(email)
        password_field.send_keys(password)

        submit_button.send_keys(Keys.ENTER)
        # The cookie named ``sessionid`` means a user is authenticated.
        sessionid_cookie = self.browser.get_cookie('sessionid')
        self.assertIsNotNone(sessionid_cookie)
        self.assertTrue(sessionid_cookie.get('value'))

    def tearDown(self) -> None:
        """Hook method for deconstructing the test fixture after testing it."""
        self.browser.quit()
