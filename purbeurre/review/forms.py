from django import forms

from .models import Review


class CreateReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['title', 'content', 'rating']

    def save(self, *, commit: bool = False, **kwargs):
        user = kwargs.pop('user')
        product_id = kwargs.pop('product_id')

        instance = super(CreateReviewForm, self).save(commit)
        instance.user = user
        instance.product_id = product_id
        instance.save()

        return instance
