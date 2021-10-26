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
    __name__ = "UserSubstitute"
    
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

    # Timestamps columns
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f"{self.original_product.name} substitué par {self.substitute_product.name}"

    def __repr__(self):
        return "<{} '{}, {}'>".format(
            self.__name__,
            self.original_product_id,
            self.substitute_product_id
        )
