from django.db.models import Count
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import reverse, redirect, get_object_or_404, render
from django.views import generic

from product.models import Product
from .models import UserSubstitute
from .forms import UserSubstituteCreateForm


class UserSubstituteIndexView(LoginRequiredMixin, generic.ListView):
    model = UserSubstitute
    template_name = 'substitute/index.html'
    context_object_name = 'substitutes'
    paginate_by = 6

    def get_queryset(self):
        user = self.request.user

        return UserSubstitute.objects.filter(user_id=user.pk)


class ProductSubstituteSearchListView(LoginRequiredMixin, generic.ListView):
    model = Product
    template_name = 'substitute/search.html'
    context_object_name = 'substitutes'
    paginate_by = 6

    original_product: Product

    def setup(self, request, *args, **kwargs):
        """Initialize attributes shared by all view methods."""
        super().setup(request, *args, **kwargs)
        # Get the product in setup to avoid a double query to the db
        # One in ``get_queryset`` and the second in ``get_context_data``.
        product_id = self.request.GET.get('pid')
        self.original_product = get_object_or_404(Product, pk=product_id)

    def get_queryset(self):
        """Return the list of items for this view.

        The return value must be an iterable and may be an instance of
        `QuerySet` in which case `QuerySet` specific behavior will be enabled.
        """
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
        """Get the context for this view."""
        ctx = super().get_context_data(object_list=object_list, **kwargs)
        skip = (int(self.request.GET.get('page', 1)) - 1) * 6

        already_substituted_ids = UserSubstitute.objects.filter(
            user_id=self.request.user.pk,
            original_product_id=self.original_product.pk,
            substitute_product_id__in=self.get_queryset()[skip:skip + 6]
        ).values_list('substitute_product_id', flat=True)

        adds = {
            "already_substituted_ids": already_substituted_ids,
            "meta": {
                "product": self.original_product,
            }
        }

        return {**ctx, **adds}  # Merge the dicts


@login_required
def save_substitute(request):
    """Register a substitute to `user_substitute`

    Create a new 'user substitute' composed of two products.
    """
    data = {"user": request.user, **request.POST.dict()}

    form = UserSubstituteCreateForm(data)

    if form.is_valid():
        form.save()

    return redirect(reverse('substitute:index'))


@login_required
def delete_substitute(request, substitute_id):
    """Delete a user substitute."""
    user = request.user
    user_substitute = UserSubstitute.objects.get(pk=substitute_id)

    if user.id != user_substitute.user_id:
        return render(request, 'substitute/index.html', status=403)

    user_substitute.delete()

    return redirect(reverse('substitute:index'))
