from django.db import models
from django.conf import settings

from product.models import Product


class UserSubstitute(models.Model):
    """UserSubstitute model

    Attributes:
        user_id (int): The ID of the user to which this substitute belongs to.
        original_product_id (int): The original product which is substitued.
        substitute_product_id (int): The product which substitute the original.
        created_at (str): The datetime where the substitute has been created.
        updated_at (str): The datetime where the substitute last update occurs.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    original_product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="original_product_id",
    )
    substitute_product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="substitute_product_id",
    )

    def __repr__(self):
        return "<{} '{}, {}'".format(
            self.__name__,
            self.original_product_id,
            self.substitute_product_id
        )
