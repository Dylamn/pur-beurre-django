from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait


class SeleniumServerTestCase(LiveServerTestCase):
    def setUp(self) -> None:  # pragma: no cover
        """Hook method for setting up the test fixture before exercising it."""
        super(SeleniumServerTestCase, self).setUp()

        chrome_options = Options()
        chrome_options.headless = True  # Run Chrome browser in a headless environment (without visible UI)
        chrome_options.add_argument("--no-sandbox")  # bypass OS security model
        chrome_options.add_argument("--disable-dev-shm-usage")  # overcome limited resource problems

        self.browser = webdriver.Chrome(chrome_options=chrome_options)
        self.wait = WebDriverWait(self.browser, timeout=5)

    def tearDown(self) -> None:
        """Hook method for deconstructing the test fixture after testing it."""
        self.browser.quit()

    def assertElementExists(self, xpath, msg=None) -> None:  # pragma: no cover
        try:
            self.browser.find_element_by_xpath(xpath)
        except NoSuchElementException as ex:
            self.assertIsNotNone(None, msg or ex.msg)

    def assertElementNotExists(self, xpath, msg=None) -> None:  # pragma: no cover
        try:
            element = self.browser.find_element_by_xpath(xpath)
            self.assertIsNone(element, msg or f'Element located (xpath): "{xpath}"')
        except NoSuchElementException:
            self.assertTrue(True)

    def login(self, *, email: str, password: str) -> None:
        """Log in a user with given credentials."""
        self.client.login(email=email, password=password)
        cookie = self.client.cookies.get('sessionid')

        if self.live_server_url not in self.browser.current_url:
            # Selenium will set cookie domain based on current page domain.
            self.browser.get(self.live_server_url)

        self.browser.add_cookie({'name': 'sessionid', 'value': cookie.value, 'path': '/', 'secure': False})
        self.browser.refresh()

    def e2e_login(self, *, email: str, password: str) -> None:
        """Log in the user through the login page like a real user."""
        self.assertTrue(
            "Login" in self.browser.title,
            msg="`e2e_login` method need the webdriver to be located on the login page before being called."
        )
        current_url = self.browser.current_url

        email_field = self.browser.find_element_by_id('username')
        password_field = self.browser.find_element_by_id('password')
        login_page_button = self.browser.find_element_by_id('login_button')

        email_field.send_keys(email)
        password_field.send_keys(password)
        login_page_button.send_keys(Keys.ENTER)

        self.wait.until(
            expected_conditions.url_changes(current_url)
        )
