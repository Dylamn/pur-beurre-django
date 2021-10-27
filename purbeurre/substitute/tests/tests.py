from django.test import TestCase
from django.shortcuts import reverse

from account.tests.factories import UserFactory
from product.tests.factories import ProductFactory, CategoryFactory
from .factories import UserSubstituteFactory


# Create your tests here.
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

    def test_user_substitute_list_with_results(self) -> None:
        """Test the view context and pagination."""
        user_substitutes = UserSubstituteFactory.create_batch(size=10, user=self.user)

        response = self.client.get(self.url)
        ctx_substitutes = response.context['substitutes']

        self.assertEqual(200, response.status_code)
        self.assertEqual(6, len(ctx_substitutes))
        self.assertQuerysetEqual(ctx_substitutes, user_substitutes[:6])


class SubstituteSearchListViewTests(TestCase):
    def setUp(self) -> None:
        self.user = UserFactory()
        self.client.force_login(self.user)
        self.original_product_categories = CategoryFactory.create_batch(5)
        self.original_product = ProductFactory(categories=self.original_product_categories)
        self.url = reverse('substitute:search') + f"?pid={self.original_product.pk}"

    def test_substitute_search_template(self):
        """Test that the template used is the expected ones."""
        response = self.client.get(self.url)

        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, template_name='substitute/search.html')

    def test_substitute_search_list(self):
        """Test the substitute list search."""
        n_substitutes = 3
        similar_products = ProductFactory.create_batch(
            categories=self.original_product_categories, size=n_substitutes
        )
        different_products = ProductFactory.create_batch(
            categories=CategoryFactory.create_batch(5), size=4
        )

        response = self.client.get(self.url)
        substitutes = response.context['substitutes']

        self.assertEqual(200, response.status_code)
        self.assertEqual(n_substitutes, response.context['paginator'].count)

        self.assertQuerysetEqual(substitutes, similar_products)
        # Verify that any `different_products` are not present in the results.
        map(lambda item: self.assertNotIn(item, substitutes), different_products)
