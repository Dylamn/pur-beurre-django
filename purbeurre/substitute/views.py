from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import reverse, render, get_object_or_404
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.views import generic
from django.contrib.auth.decorators import login_required

from product.models import Product
from .models import UserSubstitute


class UserSubstituteIndexView(generic.ListView):
    model = UserSubstitute
    template_name = 'substitute/index.html'
    context_object_name = 'substitutes'


@login_required
def search_substitutes(request):
    page = request.GET.get('page', 1)
    product_id = request.GET.get('pid')
    original_product = get_object_or_404(Product, pk=product_id)

    category_ids = list(
        original_product.categories.values_list('id', flat=True)
    )

    # TODO: Duplicates appears in the results, probably
    #  caused by the `categories__in` filter.
    substitute_list = Product.objects.filter(
        categories__in=category_ids,
        nutriscore_grade__lt=original_product.nutriscore_grade
    ).exclude(
        pk=original_product.pk
    ).order_by(
        '-categories__id', "nutriscore_grade"
    )

    paginator = Paginator(substitute_list, 6)

    try:
        substitutes = paginator.page(page)
    except PageNotAnInteger:
        substitutes = paginator.page(1)
    except EmptyPage:
        substitutes = paginator.page(paginator.num_pages)

    ctx = {
        "substitutes": substitutes,
        "meta": {
            "product": original_product
        }
    }

    return render(request, 'substitute/search.html', context=ctx)


@login_required
def save_product(request):
    wants_json = request.headers.get('Accept') == 'application/json'

    UserSubstitute.objects.create({
        'user_id': request.user.pk,
        'original_product_id': request.POST.get('original_product_id'),
        'substitute_product_id': request.POST.get('substitute_product_id'),
    })

    if not wants_json:
        return HttpResponseRedirect(reverse('substitute:index'))

    body = {
        "status": "created",
        "message": "The product has been correctly saved.",
    }

    return JsonResponse(body, status=201)
