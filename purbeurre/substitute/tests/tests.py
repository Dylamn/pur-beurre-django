from unittest import mock

from algoliasearch_django.decorators import disable_auto_indexing
from django.core.management import call_command
from django.test import TestCase, TransactionTestCase, tag
from django.shortcuts import reverse
from selenium.webdriver.common.keys import Keys

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


class SeleniumTests(SeleniumServerTestCase):
    fixtures = ['users', 'products']

    @classmethod
    def setUpClass(cls):
        super(SeleniumTests, cls).setUpClass()

    # TODO: Finish test implementation
    @mock.patch("product.views.raw_search", side_effect=algolia_mock_responses, autospec=True)
    def test_add_a_substitute_with_login(self, _mock: mock.MagicMock):
        qs = "?query=Riz&page=1"
        url = self.live_server_url + reverse('product:search') + qs

        self.browser.get(url)

        a_href_substitute = self.browser.find_element_by_xpath(
            "//div[@class='product-header']/a/div/span[.='B' or .='C' or .='D' or .= 'E']"
            "/ancestor::div[@class='product-header']/parent::node()/div[@class='product-info']/a"
        )

        a_href_substitute.click()

        self.assertTrue(True)
        print(self.browser.page_source)
