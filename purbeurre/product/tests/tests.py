import json
from pathlib import Path
from unittest import mock

from django.test import TestCase
from django.urls import reverse

from product.models import Product, Category
from .factories import CategoryFactory, ProductFactory


def algolia_mock_responses(model, query: str = "", params=None):
    """Function used for the return value of the mocked raw_search function."""
    if params is None:
        params = {}

    if query.lower() == 'riz':
        test_path = Path().absolute()

        if model is Product:
            test_path = test_path / 'product/tests/hits.json'

        with open(test_path, 'r') as f:
            return json.load(f)

    return {
        'hits': [],
        'nbHits': 0,
        'page': 0,
        'nbPages': 0,
        'hitsPerPage': 6,
        'exhaustiveNbHits': True,
        'query': 'NoResultsExpected',
        'params': 'query=NoResultsExpected&hitsPerPage=6',
        'renderingContent': {},
        'processingTimeMS': 2
    }


class ProductModelTests(TestCase):
    def test_absolute_url_method(self):
        p = Product(name="Product n°1")

        self.assertTrue(p)


# We don't patch `algoliasearch_django.raw_search` because we use a from/import
# statement for the import so the raw_search is in the `product.views` namespace.
@mock.patch("product.views.raw_search",
            side_effect=algolia_mock_responses, autospec=True)
class ProductListViewTests(TestCase):
    def setUp(self) -> None:
        self.search_url = reverse('product:search')
        self.template_name = 'product/index.html'

    def test_search_request_with_results(self, _mock: mock.MagicMock):
        search = self.search_url + '?query=Riz'
        _mock.assert_not_called()
        response = self.client.get(search)
        _mock.assert_called()

        self.assertEqual(200, response.status_code)
        self.assertLessEqual(6, len(response.context['products']))

        # Verify the presence of the essential fields for listing.
        for p in response.context['products']:
            self.assertIn('name', p)
            self.assertIn('image_small_url', p)
            self.assertIn('nutriscore_grade', p)

    def test_search_request_with_zero_results(self, _mock):
        response = self.search_query("NoResultsExpected")

        self.assertEqual(200, response.status_code)
        self.assertEqual(0, len(response.context['products']))

    def search_query(self, query):
        """Call the product index view.

        The index view search products with a given query.
        """
        search = self.search_url + f"?query={query}"

        return self.client.get(search)


class ProductDetailViewTests(TestCase):
    @staticmethod
    def generate_detail_url(_id):
        """Generate the URL for accessing to the details of a given product."""
        return reverse('product:show', args=(_id,))

    def test_detail_view_with_an_existing_product(self):
        """Test that the detail view works correctly."""
        product = ProductFactory()
        url = self.generate_detail_url(product.id)

        response = self.client.get(url)

        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, template_name='product/show.html')

    def test_detail_view_product_not_found(self):
        """Test that the product detail view returns a 404 not found page."""
        url = self.generate_detail_url(0)

        response = self.client.get(url)

        self.assertEqual(404, response.status_code)
        self.assertTemplateUsed(response, template_name='product/404.html')