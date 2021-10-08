from django.db.models import Count
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import reverse, render, get_object_or_404
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required

from product.models import Product
from .models import UserSubstitute


class UserSubstituteIndexView(LoginRequiredMixin, generic.ListView):
    model = UserSubstitute
    template_name = 'substitute/index.html'
    context_object_name = 'substitutes'
    paginate_by = 6

    def get_queryset(self):
        user = self.request.user

        return UserSubstitute.objects.filter(user_id=user.pk)


class ProductSubstitutesListView(LoginRequiredMixin, generic.ListView):
    model = Product
    template_name = 'substitute/search.html'
    context_object_name = 'substitutes'
    paginate_by = 6

    original_product: Product

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        # Get the product in setup to avoid a double query to the db
        # One in ``get_queryset`` and the second in ``get_context_data``.
        product_id = self.request.GET.get('pid')
        self.original_product = get_object_or_404(Product, pk=product_id)

    def get_queryset(self):
        category_ids = self.original_product.categories.values_list('id', flat=True)

        return Product.objects.filter(
            categories__in=category_ids,
            nutriscore_grade__lte=self.original_product.nutriscore_grade
        ).distinct().exclude(
            pk=self.original_product.pk
        ).annotate(
            categories_count=Count('categories')
        ).order_by(
            '-categories_count', 'nutriscore_grade',
        )

    def get_context_data(self, *, object_list=None, **kwargs):
        ctx = super().get_context_data(object_list=object_list, **kwargs)
        adds = {
            "meta": {
                "product": self.original_product
            }
        }

        return {**ctx, **adds}  # Merge the dicts


@login_required
def save_substitute(request):
    wants_json = request.headers.get('Accept') == 'application/json'

    exists = UserSubstitute.objects.filter(
        user_id=request.user.pk,
        original_product_id=request.POST.get('original_product_id'),
        substitute_product_id=request.POST.get('substitute_product_id'),
    ).exists()

    if exists:
        return HttpResponseRedirect(reverse('substitute:index'))

    user_substitute = UserSubstitute.objects.create(
        user_id=request.user.pk,
        original_product_id=request.POST.get('original_product_id'),
        substitute_product_id=request.POST.get('substitute_product_id'),
    )

    if not wants_json:
        return HttpResponseRedirect(reverse('substitute:index', kwargs={'user_substitute': user_substitute}))

    body = {
        "status": "created",
        "message": "The product has been correctly saved.",
    }

    return JsonResponse(body, status=201)


@login_required
def delete_substitute(request, substitute_id):
    UserSubstitute.objects.get(pk=substitute_id)