from django.test import TestCase, LiveServerTestCase, tag
from django.shortcuts import reverse
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait

from .factories import ReviewFactory
from account.tests.factories import UserFactory
from product.tests.factories import ProductFactory
from purbeurre.tests import SeleniumServerTestCase


class ReviewViewsTests(TestCase):
    def setUp(self) -> None:
        self.user = UserFactory()

    def test_review_listing(self):
        a_product = ProductFactory()
        reviews_size = 3
        product_reviews = ReviewFactory.create_batch(size=reviews_size, product=a_product)
        another_review = ReviewFactory()

        url = reverse('product:show', args=(a_product.id,))
        response = self.client.get(url)

        ctx_reviews = response.context['reviews']
        ctx_user_review = response.context['user_review']

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='review/index.html')
        self.assertTemplateUsed(response, template_name='review/review.html', count=reviews_size)
        self.assertTemplateUsed(response, template_name='review/rating.html', count=reviews_size + 1)
        self.assertQuerysetEqual(ctx_reviews.object_list, product_reviews)
        self.assertNotIn(another_review, ctx_reviews.object_list)
        self.assertEqual(ctx_user_review, None)

    def test_get_an_existing_review(self):
        review_rating = 5
        a_review = ReviewFactory(rating=review_rating)
        url = reverse('review:review', args=(a_review.id,))
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='review/edit.html')
        self.assertTemplateUsed(response, template_name='review/form.html')
        self.assertEqual(a_review, response.context['review'])
        self.assertContains(response, a_review.title)
        self.assertContains(response, a_review.content)
        self.assertContains(response, f"rating-{review_rating}")


@tag('selenium')
class SeleniumTests(SeleniumServerTestCase):
    fixtures = ['users', 'products', 'reviews']

    @classmethod
    def setUpClass(cls):
        super(SeleniumTests, cls).setUpClass()
        # A user who has not yet created a review.
        cls.user_email = 'bob.dylan@example.com'
        cls.user_password = 'password'

    def setUp(self) -> None:
        """Hook method for setting up the test fixture before exercising it."""
        self.product = ProductFactory.create()

        chrome_options = Options()
        chrome_options.headless = True  # Run Chrome browser in a headless environment (without visible UI)
        chrome_options.add_argument("--no-sandbox")  # bypass OS security model
        chrome_options.add_argument("--disable-dev-shm-usage")  # overcome limited resource problems

        self.browser = webdriver.Chrome(chrome_options=chrome_options)
        self.wait = WebDriverWait(self.browser, timeout=5)

    def test_login_and_create_a_review(self) -> None:
        # self.login(email=self.user_email, password=self.user_password)
        review_title = 'A Beautiful thing'
        review_content = 'Lorem ipsum dolor sit amet, consectetur adipisicing elit.'
        review_rating = 4

        url = self.live_server_url + reverse('product:show', args=(self.product.id,))

        self.browser.get(url)

        self.assertTrue("Vous devez être authentifié pour pouvoir rédiger un avis." in self.browser.page_source)

        # Move to login page...
        href = f"{reverse('login')}?next={reverse('product:show', args=(self.product.id,))}"
        login_btn = self.browser.find_element_by_xpath(f"//a[@href='{href}']/button[text()='Se connecter']")
        login_btn.send_keys(Keys.ENTER)

        self.e2e_login(email=self.user_email, password=self.user_password)

        self.assertTrue("Rédiger votre avis" in self.browser.page_source)
        self.assertFalse("Votre avis" in self.browser.page_source)
        self.assertFalse(review_title in self.browser.page_source)
        self.assertFalse(review_content in self.browser.page_source)
        # print(self.browser.page_source)
        self.assertFalse(f"rating-{review_rating}" in self.browser.page_source)

        title_field = self.browser.find_element_by_id('review_title')
        content_field = self.browser.find_element_by_id('review_content')
        rating_field = self.browser.find_element_by_id('review_rating')
        submit_button = self.browser.find_element_by_id('store_review_btn')

        title_field.send_keys(review_title)
        content_field.send_keys(review_content)

        while int(rating_field.get_property('value')) != review_rating:
            rating_field.send_keys(Keys.LEFT if int(rating_field.get_property('value')) > review_rating else Keys.RIGHT)

        submit_button.send_keys(Keys.ENTER)  # Submit form

        self.assertTrue("Votre avis" in self.browser.page_source)
        self.assertTrue(review_title in self.browser.page_source)
        self.assertTrue(review_content in self.browser.page_source)
        self.assertTrue(f"rating-{review_rating}" in self.browser.page_source)

    def tearDown(self) -> None:
        """Hook method for deconstructing the test fixture after testing it."""
        self.browser.quit()
