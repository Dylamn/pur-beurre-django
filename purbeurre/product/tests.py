from django.test import TestCase
from django.urls import reverse

from .models import Product, Category


class ProductListViewTests(TestCase):
    def setUp(self) -> None:
        self.search_url = reverse('product:search')

    def test_search_request_with_results(self):
        query = "Riz"
        search = self.search_url + f"?query={query}"
        response = self.client.get(search)

        self.assertEqual(200, response.status_code)
        self.assertLessEqual(6, len(response.context['products']))

        # Verify the presence of the essential fields.
        for p in response.context['products']:
            self.assertIn('name', p)
            self.assertIn('image_small_url', p)
            self.assertIn('nutriscore_grade', p)

    def test_search_request_with_zero_results(self):
        response = self.search_query("NothingWillBeFound~0")

        self.assertEqual(200, response.status_code)
        self.assertEqual(0, len(response.context['products']))

    def search_query(self, query):
        """Call the product index view.

        The index view search products with a given query.
        """
        search = self.search_url + f"?query={query}"

        return self.client.get(search)
