from django.shortcuts import render, reverse, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views import View

from .models import Review as ReviewModel
from .forms import CreateReviewForm


class Review(View):
    form_class = CreateReviewForm
    template_name = 'review/edit.html'
    review: ReviewModel

    def setup(self, request, *args, **kwargs):
        """Initialize attributes shared by all view methods."""
        self.review = get_object_or_404(ReviewModel, pk=kwargs["pk"])

        super(Review, self).setup(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        """Retrieve a single review"""
        return render(request, template_name=self.template_name, context={"review": self.review})

    def post(self, request, *args, **kwargs):
        """Endpoint for updating/deleting an existing review"""
        payload = request.POST

        if payload.get('delete'):
            return self.delete(request, *args, **kwargs)

        form = self.form_class(request.POST or None, instance=self.review)

        if form.is_valid():
            form.save(user=request.user, product_id=self.review.product_id)
            return redirect(reverse('product:show', args=(self.review.product.id,)))

        return render(request, template_name=self.template_name, context={"review": self.review})

    def delete(self, request, *args, **kwargs):
        product_id = self.review.product.id
        self.review.delete()

        return redirect(reverse('product:show', args=(product_id,)))


@login_required
def store(request):
    form = CreateReviewForm(request.POST)
    product_id = request.POST.get('product_id')

    if form.is_valid():
        form.save(user=request.user, product_id=product_id)

    return redirect(reverse('product:show', args=(request.POST.get('product_id'),)))
