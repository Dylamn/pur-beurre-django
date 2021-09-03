from django.shortcuts import render, redirect, reverse
from django.views.generic import DetailView
from algoliasearch_django import raw_search

from .models import Product


def index(request):
    query: str = request.GET.get('query', '')

    if not query:  # No query, don't do a search request
        return redirect(reverse('home:index'))

    # Algolia search parameters
    params = {
        "hitsPerPage": 6,
    }

    response = raw_search(Product, query, params)

    ctx = {
        "products": response['hits'],
        "input_query": query,
    }

    return render(request, 'product/index.html', context=ctx)


class ProductDetailView(DetailView):
    model = Product
    template_name = 'product/show.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add a list containing the nutriscore letters
        context.setdefault('nutriscore_letters', ['a', 'b', 'c', 'd', 'e'])

        return context
