import asyncio
from time import time
from math import ceil

import httpx
from algoliasearch_django.decorators import disable_auto_indexing
from django.core.management.base import BaseCommand, CommandError
from django.utils.text import slugify

from product.models import Product, Category


class Command(BaseCommand):
    OPENFOODFACTS_BASE_URL = "https://fr-en.openfoodfacts.org"

    help = 'Populate the database of products and categories.'

    @staticmethod
    def _get_fields() -> tuple:
        """Fields that will be present in the OpenFoodFacts responses."""
        return (
            # Product fields
            'product_name', 'generic_name', 'nutriscore_grade', 'brands',
            'stores', 'url', 'image_url', 'image_small_url',
            # Category fields
            'categories', 'categories_tags',
        )

    def handle(self, *args, **options):
        start = time()
        first_page = 1
        # First index is for products added and the second is for categories.
        count = (0, 0)

        # TODO: Get ingredients too...
        params = {
            'json': True, 'action': 'process', 'page_size': 300,
            'page': first_page, 'fields': ','.join(self._get_fields()),
            'tagtype_0': 'states', 'tag_contains_0': 'contains',
            'tag_0': 'fr:checked',
        }

        response = asyncio.run(self._fetch_products(params)).pop()

        if response.status_code != 200:
            self._throw_error()

        # Get the content of the JSON body...
        payload = response.json()

        # Calculate the number of pages.
        last_page = ceil(int(payload.get('count', 0)) / params['page_size'])

        # Save the first page of products in the database.
        added = self._save_products_and_categories(payload.get('products', []))
        # Update the numbers of products/categories added.
        count = self._update_count(count, added)

        if first_page != last_page:
            # Increment the page number for the upcoming requests.
            params['page'] += 1

            # Fetch all remaining pages...
            reqs = asyncio.run(self._fetch_products(params, last_page=last_page))

            for req in reqs:
                products = req.json().get('products', [])

                added = self._save_products_and_categories(products)
                count = self._update_count(count, added)

        elapsed_time = time() - start

        self.stdout.write(
            self.style.SUCCESS(
                f"Sucessfully imported {count[0]} products "
                f"and {count[1]} categories. ({elapsed_time:.2f} seconds)"
            )
        )

    @staticmethod
    @disable_auto_indexing()
    def _save_products_and_categories(products):
        categories_added = 0
        products_added = 0

        # we named the var 'p' in order to avoid conflits with the package name.
        for p in products:
            if p.get('nutriscore_grade') is None:
                continue

            categories = p.get('categories').split(',')
            categories_tags = p.get('categories_tags')

            saved_product, recently_created = Product.objects.get_or_create(
                slug=slugify(p.get('product_name')),
                defaults={
                    "name": p.get('product_name'),
                    # We check the length of `generic_name` as on the first release
                    # no one exceeded 254 characters but one product has been updated
                    # with a generic name length greater than the maximum field length.
                    "generic_name": p.get('generic_name') if len(p.get('generic_name', '')) <= 254 else None,
                    "brands": p.get('brands'),
                    "stores": p.get('stores'),
                    "nutriscore_grade": p.get('nutriscore_grade'),
                    "url": p.get('url').strip(),
                    "image_url": p.get('image_url'),
                    "image_small_url": p.get('image_small_url'),
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

    async def _fetch_products(self, params, last_page=None):
        first_page = params.get('page', 1)
        last_page = last_page or first_page
        tasks = []

        async with httpx.AsyncClient() as client:
            for page in range(first_page, (last_page + 1)):
                # Create a new instance for each requests.
                p = params.copy()
                p['page'] = page

                tasks.append(
                    client.get(
                        f"{self.OPENFOODFACTS_BASE_URL}/cgi/search.pl",
                        params=p, timeout=10.0
                    )
                )

            reqs = await asyncio.gather(*tasks)

        return reqs

    def _throw_error(self):
        raise CommandError(
            'An error occurred when connecting to the Open Food Facts API. '
            'Please try again later.'
        )

    @staticmethod
    def _update_count(count, added):
        return tuple(map(lambda x, y: x + y, count, added))
