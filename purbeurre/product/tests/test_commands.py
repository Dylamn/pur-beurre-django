import json
from pathlib import Path
from unittest import mock

from django.test import TestCase
from django.core.management import call_command

from product.management.commands.populate import Command as PopulateCommand
from product.models import Product


class FakeJsonResponse:
    def __init__(self, data, status=200):
        self._data = data
        self._status_code = status

    @property
    def status_code(self):
        return self._status_code

    def json(self):
        return self._data


def get_off_json_fragment(page=1):
    """Get the OFF JSON fragment used for tests

    OFF acronym's stand for `Open Food Facts`.
    Those JSON fragments has been snapshoted at 2021 November.
    """
    test_path = Path().resolve() / f"product/tests/off_json_fragment_{page}.json"

    with open(test_path, 'r') as file:
        return json.load(file)


async def fetch_products_mock(self, params, last_page=None) -> list:
    """Only used for mocking the `_fetch_product` of the `populate` command."""
    page = 1 if last_page is None else 2

    fake_json = FakeJsonResponse(get_off_json_fragment(page=page))

    return [fake_json]


def algolia_reindex_fake(self, *args, **options):
    """Fake the `algolia_reindex` command."""
    print("Reindexing Indices...")


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
