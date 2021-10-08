import factory
from faker import Faker
from django.utils.text import slugify
from django.utils import timezone

from product.models import Category, Product

fake = Faker()


class TimestampFactory:
    created_at = factory.LazyFunction(timezone.now)
    updated_at = factory.LazyFunction(timezone.now)


class CategoryFactory(TimestampFactory, factory.django.DjangoModelFactory):
    class Meta:
        model = Category

    name = factory.Sequence(lambda n: f"Category n°{n}")
    tag = "{0}:{1}".format(fake.language_code(), slugify(factory.SelfAttribute('name')))


class ProductFactory(TimestampFactory, factory.django.DjangoModelFactory):
    class Meta:
        model = Product

    name = factory.Sequence(lambda n: f"Product n°{n}")
    slug = slugify(factory.SelfAttribute('name'))
    generic_name = f"Generic {factory.SelfAttribute('name')}"

    nutriscore_grade = fake.random_element(elements=('a', 'b', 'c', 'd', 'e'))

    url = fake.url(schemes=['https'])
    image_url = fake.image_url()
    image_small_url = fake.image_url()

    @factory.lazy_attribute
    def brands(self):
        brand_names = [fake.company() for _ in range(fake.random_int(min=1, max=4))]

        return ','.join(brand_names)

    @factory.lazy_attribute
    def stores(self):
        brand_names = [fake.company() for _ in range(fake.random_int(min=1, max=4))]

        return ','.join(brand_names)
