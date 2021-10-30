from algoliasearch_django import AlgoliaIndex
from algoliasearch_django.decorators import register

from .models import Product


@register(Product)
class ProductIndex(AlgoliaIndex):
    # Specify the fields that should be included in the index.
    fields = (
        'name', 'generic_name', 'brands', 'category_names', 'nutriscore_grade',
        'image_url', 'image_small_url',
    )

    # Specify the settings of the index.
    settings = {
        'searchableAttributes': [
            'name', 'generic_name', 'brands', 'category_names'
        ],
        'customRanking': [
            'asc(nutriscore_grade)', 'asc(name)',
        ]
    }
