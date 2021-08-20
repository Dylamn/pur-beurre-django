from time import perf_counter
from math import ceil

import requests
from django.core.management.base import BaseCommand, CommandError
from django.utils.text import slugify

from product.models import Product, Category


class Command(BaseCommand):
    OPENFOODFACTS_BASE_URL = "https://fr-en.openfoodfacts.org"

    help = 'Populate the database of products and categories.'

    _fields = [
        # Product fields
        'product_name', 'generic_name', 'nutriscore_grade', 'brands',
        'stores', 'url',
        # Category fields
        'categories', 'categories_tags',
    ]

    def add_arguments(self, parser):
        pass

    # TODO: Rewrite as async function with an asynchronous HTTP library.
    def handle(self, *args, **options):
        start = perf_counter()
        page = 1
        # First index is for products added and the second is for categories.
        count = (0, 0)

        params = {
            'json': True, 'action': 'process', 'page_size': 1000, 'page': page,
            'fields': ','.join(self._fields), 'tagtype_0': 'states',
            'tag_contains_0': 'contains', 'tag_0': 'fr:checked',
        }

        response = self._get_products(params)

        if not response.ok:
            self._throw_error()

        # Get the content of the JSON body...
        payload = response.json()

        # Calculate the number of pages.
        last_page = ceil(int(payload.get('count')) / params['page_size'])

        # We'll use a while loop in order to fetch all products.
        # We can't pull all products in a single request
        # because the maximum page size is 1000.
        while page < last_page:
            products = payload.get('products', [])

            added = self._save_products_and_categories(products)
            count = self._update_count(count, added)

            page += 1
            params['page'] = page

            response = self._get_products(params)

            if not response.ok:
                self._throw_error()

            payload = response.json()

        elapsed_time = perf_counter() - start

        self.stdout.write(
            self.style.SUCCESS(
                f"Sucessfully imported {str(count[0])} products "
                f"and {str(count[1])} categories. "
                f"(took {elapsed_time:.2f}s)"
            )
        )

    @staticmethod
    def _save_products_and_categories(products):
        categories_added = 0
        products_added = 0

        # we named the var 'p' in order to avoid conflits with the package name.
        for p in products:
            if not p.get('nutriscore_grade'):
                continue

            categories = p.get('categories').split(',')
            categories_tags = p.get('categories_tags')

            saved_product, recently_created = Product.objects.get_or_create(
                slug=slugify(p.get('product_name')),
                defaults={
                    "name": p.get('product_name'),
                    "generic_name": p.get('generic_name'),
                    "brands": p.get('brands'),
                    "stores": p.get('stores'),
                    "nutriscore_grade": p.get('nutriscore_grade'),
                    "url": p.get('url').strip(),
                }
            )

            if recently_created:
                products_added += 1

            for name, tag in zip(categories, categories_tags):
                category, newly_created = Category.objects.get_or_create(
                    tag=tag, defaults={"name": name.strip()}
                )

                if newly_created:  # The category is newly created
                    categories_added += 1

                saved_product.categories.add(category)

        return products_added, categories_added

    def _get_products(self, params):
        return requests.get(
            f"{self.OPENFOODFACTS_BASE_URL}/cgi/search.pl", params=params
        )

    def _throw_error(self):
        raise CommandError(
            'An error occurred when connecting to the Open Food Facts API. '
            'Please try again later.'
        )

    @staticmethod
    def _update_count(count, added):
        return count[0] + added[0], count[1] + added[1]

