from django import forms
from django.utils.translation import gettext_lazy as _
from substitute.models import UserSubstitute


class UserSubstituteCreateForm(forms.ModelForm):
    class Meta:
        model = UserSubstitute
        fields = ('user', 'original_product', 'substitute_product',)

    def clean_substitute_product(self):
        original_product_id = self.cleaned_data.get('original_product')
        substitute_product_id = self.cleaned_data.get('substitute_product')

        if original_product_id == substitute_product_id:
            msg = _("The ID must be different from the one in the '{}' field.")
            self.add_error("original_product", msg.format("substitute_product"))
            self.add_error("substitute_product", msg.format("original_product"))

        return substitute_product_id
