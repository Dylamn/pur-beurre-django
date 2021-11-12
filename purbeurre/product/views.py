from django.shortcuts import render, redirect, reverse
from django.views.generic import DetailView
from algoliasearch_django import raw_search

from .models import Product


def index(request):
    query: str = request.GET.get('query', '')
    current_page = int(request.GET.get('page', 1))

    if not query:  # No query, don't do a search request
        return redirect(reverse('home:index'))

    # Algolia search parameters
    params = {
        "hitsPerPage": 6,
        # We subtract by one because algolia starts at index 0 for pages.
        "page": current_page - 1,
    }

    response = raw_search(Product, query, params)

    ctx = {
        "products": response['hits'],

        "meta": {
            "input_query": query,
            "page": current_page,
            "previous_page": current_page - 1 or None,
            "next_page": current_page + 1 if response['nbPages'] >= current_page + 1 else None,
            "last_page": response['nbPages'],
            "page_range": (range(1, response['nbPages'] + 1)),
            "per_page": response['hitsPerPage'],
            "total": response['nbHits'],
        }
    }

    return render(request, 'product/index.html', context=ctx)


class ProductDetailView(DetailView):
    model = Product
    template_name = 'product/show.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # Add a list containing the nutriscore letters
        ctx.setdefault('nutriscore_letters', ['a', 'b', 'c', 'd', 'e'])

        return ctx
