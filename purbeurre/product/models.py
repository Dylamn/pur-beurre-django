from django.db import models
from django.urls import reverse


class Category(models.Model):
    __name__ = "Category"

    name = models.CharField(max_length=254)
    tag = models.CharField(max_length=128, unique=True)

    # Timestamps columns
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Relationships
    products = models.ManyToManyField('Product')

    def __str__(self):
        return self.name

    def __repr__(self):
        return "<{} '{}'>".format(self.__class__, self.id)


# Create your models here.
class Product(models.Model):
    __name__ = "Product"

    # Specific columns
    name = models.CharField(max_length=254)
    slug = models.SlugField(max_length=254)
    generic_name = models.CharField(max_length=254, null=True)
    brands = models.CharField(max_length=128, null=True)
    stores = models.CharField(max_length=128, null=True)
    nutriscore_grade = models.CharField(max_length=1)
    url = models.CharField(max_length=255, null=True)
    image_url = models.CharField(max_length=255, null=True)
    image_small_url = models.CharField(max_length=255, null=True)

    # Timestamps columns
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Relationships
    categories = models.ManyToManyField(Category)

    def get_absolute_url(self):
        """Returns the url to access a detail record for this Product."""
        return reverse('product:show', args=(self.slug,))

    def category_names(self):
        """Proxy method for algolia indexing."""
        return [str(category) for category in self.categories.all()]

    def __str__(self):
        return self.name

    def __repr__(self):
        return "<{} '{}'>".format(self.__name__, self.id)
