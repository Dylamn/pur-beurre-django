from django.shortcuts import reverse
from django.test import TestCase, tag
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait

from account.models import User
from account.tests.factories import UserFactory
from product.tests.factories import ProductFactory
from purbeurre.tests import SeleniumServerTestCase
from .factories import ReviewFactory
from ..models import Review


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

    def test_update_an_existing_review(self):
        self.client.force_login(user=self.user)
        a_review = ReviewFactory(user=self.user, rating=4)
        updated_values = {
            'title': a_review.title[::-1],
            'content': a_review.content[::-1],
            'rating': a_review.rating + 1
        }

        response = self.client.post(reverse('review:review', args=(a_review.id,)), data=updated_values)

        self.assertRedirects(response, expected_url=reverse('product:show', args=(a_review.product_id,)))

        a_review.refresh_from_db()
        self.assertEqual(a_review.title, updated_values['title'])
        self.assertEqual(a_review.content, updated_values['content'])
        self.assertEqual(a_review.rating, updated_values['rating'])

    def test_delete_an_existing_review(self):
        self.client.force_login(user=self.user)
        review_to_delete = ReviewFactory(user=self.user)

        response = self.client.post(reverse('review:review', args=(review_to_delete.id,)), data={'delete': True})

        self.assertRedirects(response, expected_url=reverse('product:show', args=(review_to_delete.product_id,)))
        self.assertFalse(Review.objects.filter(pk=review_to_delete.id).exists())


@tag('selenium')
class SeleniumTests(SeleniumServerTestCase):
    fixtures = ['users', 'products', 'reviews']

    @classmethod
    def setUpClass(cls):
        super(SeleniumTests, cls).setUpClass()
        # A user who has not yet created a review.
        cls.user_email = 'bob.dylan@example.com'
        cls.user_password = 'password'

    @staticmethod
    def set_range_input_value(field, value):
        """Set the value property of a "range" type input."""
        while int(field.get_property('value')) != value:
            field.send_keys(
                Keys.LEFT if int(field.get_property('value')) > value else Keys.RIGHT
            )

    @staticmethod
    def get_review_rating_xpath(rating) -> str:
        """Get the "rating element" xpath of the authenticated user's review."""
        return f"//div[@id='my_review']/article/header/p/span[@class='rating rating-{rating}']"

    def setUp(self) -> None:
        """Hook method for setting up the test fixture before exercising it."""
        self.product = ProductFactory.create()

        chrome_options = Options()
        chrome_options.headless = True  # Run Chrome browser in a headless environment (without visible UI)
        chrome_options.add_argument("--no-sandbox")  # bypass OS security model
        chrome_options.add_argument("--disable-dev-shm-usage")  # overcome limited resource problems

        self.browser = webdriver.Chrome(chrome_options=chrome_options)
        self.wait = WebDriverWait(self.browser, timeout=5)

    def tearDown(self) -> None:
        """Hook method for deconstructing the test fixture after testing it."""
        self.browser.quit()

    def test_login_and_create_a_review(self) -> None:
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
        self.assertElementNotExists(self.get_review_rating_xpath(review_rating))

        title_field = self.browser.find_element_by_id('review_title')
        content_field = self.browser.find_element_by_id('review_content')
        rating_field = self.browser.find_element_by_id('review_rating')
        submit_button = self.browser.find_element_by_id('store_review_btn')

        title_field.send_keys(review_title)
        content_field.send_keys(review_content)

        self.set_range_input_value(rating_field, value=review_rating)

        submit_button.send_keys(Keys.ENTER)  # Submit form

        self.assertTrue("Votre avis" in self.browser.page_source)
        self.assertTrue(review_title in self.browser.page_source)
        self.assertTrue(review_content in self.browser.page_source)
        self.assertTrue(f"rating-{review_rating}" in self.browser.page_source)
        self.assertElementExists(self.get_review_rating_xpath(review_rating))

    def test_edit_a_review(self):
        user = User.objects.get(email=self.user_email)
        the_review = ReviewFactory(user=user, product=self.product, rating=1)
        url = self.live_server_url + reverse('product:show', args=(the_review.product_id,))

        new_review_title = "I've updated my review!!"
        new_review_content = 'Updated e2e content!'
        new_review_rating = 5

        self.browser.get(url)
        self.login(email=self.user_email, password=self.user_password)

        self.assertTrue("Votre avis" in self.browser.page_source)
        self.assertTrue(the_review.title in self.browser.page_source)
        self.assertTrue(the_review.content in self.browser.page_source)
        self.browser.find_element_by_xpath(self.get_review_rating_xpath(the_review.rating))

        href = f"{reverse('review:review', args=(the_review.id,))}"
        button = self.browser.find_element_by_xpath(f"//a[@href='{href}']/button[text()='Modifier']")
        button.send_keys(Keys.ENTER)

        self.assertTrue("Modifier mon avis" in self.browser.title)

        title_field = self.browser.find_element_by_id("review_title")
        content_field = self.browser.find_element_by_id("review_content")
        rating_field = self.browser.find_element_by_id("review_rating")
        submit_button = self.browser.find_element_by_xpath("//button[text()='Soumettre']")

        self.set_range_input_value(rating_field, value=new_review_rating)

        title_field.send_keys(new_review_title)
        content_field.send_keys(new_review_content)

        submit_button.send_keys(Keys.ENTER)

        self.assertTrue(new_review_title in self.browser.page_source)
        self.assertTrue(new_review_content in self.browser.page_source)
        self.assertElementExists(self.get_review_rating_xpath(new_review_rating))

    def test_delete_a_review(self):
        user = User.objects.get(email=self.user_email)
        the_review = ReviewFactory(user=user, product=self.product)
        url = self.live_server_url + reverse('product:show', args=(the_review.product_id,))

        self.login(email=self.user_email, password=self.user_password)

        self.browser.get(url)

        self.assertTrue("Votre avis" in self.browser.page_source)
        self.assertTrue(the_review.title in self.browser.page_source)
        self.assertTrue(the_review.content in self.browser.page_source)
        self.assertElementExists(self.get_review_rating_xpath(the_review.rating))

        delete_button = self.browser.find_element_by_xpath(
            "//div[@id='my_review']/*/*/*/form[@class='delete-review-form']/button[@id='delete_btn']"
        )

        delete_button.send_keys(Keys.ENTER)
        alert = Alert(self.browser)

        alert.accept()

        self.assertFalse("Votre avis" in self.browser.page_source)
        self.assertFalse(the_review.title in self.browser.page_source)
        self.assertFalse(the_review.content in self.browser.page_source)
        self.assertElementNotExists(self.get_review_rating_xpath(the_review.rating))
        self.assertTrue("Rédiger votre avis" in self.browser.page_source)
