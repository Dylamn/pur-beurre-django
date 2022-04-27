from unittest import mock

from django.test import TestCase
from django.core.management import call_command

from product.tests.utils import fetch_products_mock, algolia_reindex_fake
from product.management.commands.populate import Command as PopulateCommand
from product.models import Product


@mock.patch.object(PopulateCommand, "_fetch_products",
                   side_effect=fetch_products_mock, autospec=True)
class CommandsTestCase(TestCase):
    def test_populate_command(self, _mock: mock.MagicMock):
        """Test the custom command `populate`."""
        args = []
        opts = {"pagesize": 4}

        # Check that no products already exists
        self.assertQuerysetEqual(Product.objects.all(), [])

        # Call the `populate` command.
        # For the test, we'll limit the numbers of products
        # and expect an import of eight products.
        with mock.patch(
                'algoliasearch_django.management.commands.algolia_reindex.Command.handle',
                new=algolia_reindex_fake
        ):
            call_command('populate', *args, **opts)

        self.assertEqual(8, Product.objects.count())
