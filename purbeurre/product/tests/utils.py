import json
from pathlib import Path

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
    pass
