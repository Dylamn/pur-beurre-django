import json
from pathlib import Path
from unittest import mock

from algoliasearch_django.decorators import disable_auto_indexing
from django.test import TestCase
from django.shortcuts import reverse

from product.models import Product
from .factories import CategoryFactory, ProductFactory


def algolia_mock_responses(model, query: str = "", params=None):  # pragma: no cover
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
        'query': query,
        'params': f'query={query}&hitsPerPage=6',
        'renderingContent': {},
        'processingTimeMS': 2
    }


class ProductModelTests(TestCase):
    @disable_auto_indexing()
    def test_absolute_url_method(self):
        """Test that the ``get_absolute_url`` use the right template."""
        p = ProductFactory(categories=(CategoryFactory(),))
        url = p.get_absolute_url()

        response = self.client.get(url)

        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, template_name='product/show.html')

    def test_brands_list_method(self):
        """Test the ``brands_list`` method."""
        brands = "Brand1,Brand2,Brand3"
        p = ProductFactory.build(brands=brands)

        self.assertEqual(brands.split(','), p.brands_list())

    def test_stores_list_method(self):
        """Test the ``stores_list`` method."""
        stores = "Store1,Store2,Store3,Store4"
        p = ProductFactory.build(stores=stores)

        self.assertEqual(stores.split(','), p.stores_list())

    def test_str_dunder_method(self):
        """Test that the `__str__` method uses the name of the product."""
        p_name = "Product.toString"
        p = ProductFactory.build(name=p_name)

        self.assertEqual(p_name, str(p))


# We don't patch `algoliasearch_django.raw_search` because we use a from/import
# statement for the import so the raw_search is in the `product.views` namespace.
@mock.patch("product.views.raw_search",
            side_effect=algolia_mock_responses, autospec=True)
class ProductListViewTests(TestCase):
    def setUp(self) -> None:
        self.search_url = reverse('product:search')
        self.template_name = 'product/index.html'

    def test_search_request_redirect_when_no_query_provided(self, _mock: mock.MagicMock):
        _mock.assert_not_called()
        response = self.client.get(self.search_url)

        # mock still not called because we redirect
        # before the call to Algolia when no query is provided.
        _mock.assert_not_called()

        self.assertRedirects(response, expected_url='/')

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
        self.assertQuerysetEqual(response.context['products'], [])

    def search_query(self, query):
        """Call the product index view.

        The index view search products with a given query.
        """
        search = f"{self.search_url}?query={query}"

        return self.client.get(search)


class ProductDetailViewTests(TestCase):
    @staticmethod
    def generate_detail_url(_id):
        """Generate the URL for accessing to the details of a given product."""
        return reverse('product:show', args=(_id,))

    @disable_auto_indexing()
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
        self.assertTemplateNotUsed(response, template_name='product/show.html')
        self.assertTemplateUsed(response, template_name='product/404.html')
