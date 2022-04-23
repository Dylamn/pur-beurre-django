from django.db import models

from account.models import User
from product.models import Product


# Create your models here.
class Review(models.Model):
    """Review model

    Attributes:
        id (int): The identifier of the review.
        title (str): The title of the review.
        content (str): The detailled review description.
        product_id (int): The product on which this review is for.
        created_at (str): The datetime where the review has been created.
        updated_at (str): The datetime where the review last update occurs.
    """
    class Meta:
        ordering = ['id']

    title = models.CharField(max_length=64)
    content = models.TextField(null=False)

    rating = models.PositiveSmallIntegerField()

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=False
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        null=False
    )
    # Timestamps columns
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Review n°{self.pk}'