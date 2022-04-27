from typing import Tuple
from unittest import mock
from urllib.parse import quote_plus

from algoliasearch_django.decorators import disable_auto_indexing
from django.shortcuts import reverse
from django.test import TestCase, TransactionTestCase, tag
from selenium.webdriver.remote.webelement import WebElement

from account.tests.factories import UserFactory
from product.tests.factories import ProductFactory, CategoryFactory
from product.tests.utils import algolia_mock_responses
from purbeurre.tests import SeleniumServerTestCase
from .factories import UserSubstituteFactory
from ..models import UserSubstitute


class UserSubstituteListViewTests(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        """Load initial data for the TestCase."""
        cls.url = reverse('substitute:index')

    def setUp(self) -> None:
        self.user = UserFactory()
        self.client.force_login(self.user)

    def test_user_substitute_list_template(self) -> None:
        """Assert that the right template is used."""
        response = self.client.get(self.url)

        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, template_name='substitute/index.html')
        self.assertQuerysetEqual(response.context['substitutes'], [])

    @disable_auto_indexing()
    def test_user_substitute_list_with_results(self) -> None:
        """Test the view context and pagination."""
        user_substitutes = UserSubstituteFactory.create_batch(size=10, user=self.user)

        response = self.client.get(self.url)
        ctx_substitutes = response.context['substitutes']

        self.assertEqual(200, response.status_code)
        self.assertEqual(6, len(ctx_substitutes))
        self.assertQuerysetEqual(ctx_substitutes, user_substitutes[:6])


class SubstituteSearchListViewTests(TransactionTestCase):
    reset_sequences = True

    @disable_auto_indexing()
    def setUp(self) -> None:
        self.user = UserFactory()
        self.client.force_login(self.user)
        self.original_product_categories = CategoryFactory.create_batch(5)
        self.original_product = ProductFactory(categories=self.original_product_categories)
        self.url = reverse('substitute:search') + f"?pid={self.original_product.pk}"

    def test_substitute_search_template(self) -> None:
        """Test that the template used is the expected ones."""
        response = self.client.get(self.url)

        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, template_name='substitute/search.html')

    @disable_auto_indexing()
    def test_empty_substitute_search_list(self) -> None:
        """Test that products that has no shared categories doesn't appear.

        Also test that empty substitute list result is also handled.
        """
        ProductFactory.create_batch(
            size=10, categories=CategoryFactory.create_batch(3),
        )

        response = self.client.get(self.url)

        self.assertEqual(200, response.status_code)
        self.assertQuerysetEqual([], response.context['substitutes'])
        self.assertContains(response, f"<h5>Aucun substituts trouvé pour « {self.original_product.name} »</h5>")

    @disable_auto_indexing()
    def test_substitute_search_list(self) -> None:
        """Test the substitute list search."""
        n_substitutes = 3
        similar_products = ProductFactory.create_batch(
            categories=self.original_product_categories, size=n_substitutes
        )
        different_products = ProductFactory.create_batch(
            size=4, categories=CategoryFactory.create_batch(5)
        )

        response = self.client.get(self.url)
        substitutes = response.context['substitutes']

        self.assertEqual(200, response.status_code)
        self.assertEqual(n_substitutes, response.context['paginator'].count)

        self.assertQuerysetEqual(substitutes, similar_products)
        # Verify that any `different_products` are not present in the results.
        for item in different_products:
            self.assertNotIn(item, substitutes)


class SaveUserSubstituteView(TestCase):
    def setUp(self) -> None:
        self.user = UserFactory()
        self.client.force_login(self.user)
        self.url = reverse('substitute:save')

    @disable_auto_indexing()
    def test_save_substitute(self) -> None:
        original_product, product_substitute = ProductFactory.create_batch(
            size=2, categories=CategoryFactory.create_batch(3)
        )
        data = {
            "original_product": original_product.id,
            "substitute_product": product_substitute.id,
        }

        response = self.client.post(self.url, data=data)

        self.assertRedirects(response, expected_url=reverse('substitute:index'))
        self.assertTrue(
            UserSubstitute.objects.filter(
                user_id=self.user.pk,
                original_product_id=original_product.id,
                substitute_product_id=product_substitute.id
            ).exists()
        )

    @disable_auto_indexing()
    def test_save_substitute_already_exists(self):
        original_product, substitute_product = ProductFactory.create_batch(
            size=2, categories=CategoryFactory.create_batch(2)
        )

        count_queryset = UserSubstitute.objects.filter(
            original_product_id=original_product.id,
            substitute_product_id=substitute_product.id
        )

        # Create the substitute through its factory
        UserSubstituteFactory(
            user=self.user,
            original_product=original_product,
            substitute_product=substitute_product
        )

        # Clone/copy the queryset with the `all` method.
        self.assertEqual(1, count_queryset.all().count())

        # Try to create through the view which should fail.
        response = self.client.post(self.url, data={
            "original_product": original_product.id,
            "substitute_product": substitute_product.id,
        })

        self.assertRedirects(response, expected_url=reverse('substitute:index'))
        self.assertEqual(1, count_queryset.count())

    @disable_auto_indexing()
    def test_save_user_substitute_with_same_original_and_substitute_product(self):
        product_ = ProductFactory(categories=CategoryFactory.create_batch(2))
        data = {
            "original_product": product_.id,
            "substitute_product": product_.id,
        }

        response = self.client.post(self.url, data=data)

        self.assertRedirects(response, expected_url=reverse('substitute:index'))
        self.assertFalse(
            UserSubstitute.objects.filter(
                original_product_id=product_.id,
                substitute_product_id=product_.id,
                user_id=self.user.id
            ).exists()
        )


class DeleteUserSubstituteView(TestCase):
    @disable_auto_indexing()
    def setUp(self) -> None:
        self.user = UserFactory()
        self.client.force_login(self.user)
        self.user_substitute = UserSubstituteFactory(user=self.user)
        self.url = reverse('substitute:delete', args=(self.user_substitute.pk,))

    def test_delete_user_substitute(self) -> None:
        response = self.client.delete(self.url)

        self.assertRedirects(response, expected_url=reverse('substitute:index'))
        self.assertFalse(UserSubstitute.objects.filter(id=self.user_substitute.pk).exists())

    def test_delete_user_substitute_of_another_user_is_forbidden(self):
        another_user = UserFactory()
        self.client.logout()
        self.client.force_login(another_user)

        response = self.client.delete(self.url)

        # HTTP status should be forbidden and the user substitute stays alive.
        self.assertEqual(403, response.status_code)
        self.assertTrue(
            UserSubstitute.objects.filter(id=self.user_substitute.pk).exists()
        )


@tag('selenium')
@mock.patch("product.views.raw_search", side_effect=algolia_mock_responses, autospec=True)
class SeleniumTests(SeleniumServerTestCase):
    fixtures = ['users', 'products']

    @classmethod
    def setUpClass(cls):
        super(SeleniumTests, cls).setUpClass()
        cls.user_email = 'macgyver@example.com'
        cls.user_password = 'password'
        cls.qs = "?query=Riz&page=1"
        cls.url = cls.live_server_url + reverse('product:search') + cls.qs

    def get_substitute_element_by_xpath(self, nutriscore_letter: str) -> Tuple[WebElement, WebElement, str]:
        element = self.browser.find_element_by_xpath(
            "//div[contains(@class, 'ns-%s')]/parent::node()" % nutriscore_letter.lower()
        )
        substitute_name = element.find_element_by_xpath('h5').text
        button = element.find_element_by_xpath(
            "following-sibling::form/button/span[.='Enregistrer']/ancestor::button"
        )

        return element, button, substitute_name

    def test_add_a_substitute_through_product_listing_with_login(self, _mock: mock.MagicMock):
        _mock.assert_not_called()
        self.browser.get(self.url)
        _mock.assert_called_once()
        a_href_substitute = self.browser.find_element_by_xpath(
            "//div[@class='product-header']/a/div/span[.='B']/ancestor::a/h5[.='Riz Basmati']"
            "/ancestor::div[@class='product-header']/parent::node()/div[@class='product-info']/a"
        )
        href_substitute_value = a_href_substitute.get_attribute('href')
        pid = href_substitute_value[href_substitute_value.rindex('?'):]

        a_href_substitute.click()

        self.assertEqual(
            f"{self.live_server_url}{reverse('login')}?next={reverse('substitute:search')}{quote_plus(pid)}",
            self.browser.current_url
        )

        self.e2e_login(email=self.user_email, password=self.user_password)

        self.assertEqual(href_substitute_value, self.browser.current_url)

        _, button, substitute_name = self.get_substitute_element_by_xpath('a')
        button.click()

        self.assertEqual(self.live_server_url + reverse('substitute:index'), self.browser.current_url)

        rows = self.browser.find_elements_by_xpath('//tbody/*')
        self.assertEqual(len(rows), 1)
        [row] = rows
        self.assertTrue("Riz Basmati" in row.text)
        self.assertTrue(substitute_name in row.text)

    def test_add_a_substitute_through_product_page_and_delete_it(self, _mock: mock.MagicMock):
        product_name = 'Riz Basmati'

        self.browser.get(self.url)

        self.browser.find_element_by_xpath(
            "//div[@class='product-header']/a/div/span[.='B']/ancestor::a/h5[.='%s']/parent::node()" % product_name
        ).click()

        self.assertTrue(product_name in self.browser.title)
        self.browser.find_element_by_xpath("//button[text()='Rechercher un substitut']").click()

        self.assertTrue(f"{reverse('login')}?next={reverse('substitute:search')}" in self.browser.current_url)
        self.e2e_login(email=self.user_email, password=self.user_password)

        self.assertTrue(reverse('substitute:search') in self.browser.current_url)

        _, button, substitute_name = self.get_substitute_element_by_xpath('b')
        button.click()

        self.assertEqual(self.live_server_url + reverse('substitute:index'), self.browser.current_url)

        rows = self.browser.find_elements_by_xpath('//tbody/*')
        self.assertEqual(len(rows), 1)
        row: WebElement = rows[0]

        self.assertTrue(product_name in row.text)
        self.assertTrue(substitute_name in row.text)

        delete_button: WebElement = row.find_element_by_xpath("td[last()]/a/button[.='Supprimer']")
        delete_button.click()

        self.wait.until(lambda driver: driver.current_url == self.live_server_url + reverse('substitute:index'))

        hydrated_rows = self.browser.find_elements_by_xpath('//tbody/*')
        self.assertEqual(len(hydrated_rows), 0)
