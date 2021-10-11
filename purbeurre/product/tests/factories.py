import factory
from faker import Faker
from django.utils.text import slugify
from django.utils import timezone

from product.models import Category, Product

fake = Faker()


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category

    name = factory.Sequence(lambda n: f"Category n°{n}")
    tag = "{0}:{1}".format(fake.language_code(), slugify(factory.SelfAttribute('name')))
    created_at = factory.LazyFunction(timezone.now)
    updated_at = factory.LazyFunction(timezone.now)


class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Product

    name = factory.Sequence(lambda n: "Product%d" % n)
    slug = factory.LazyAttribute(lambda obj: slugify(obj.name))
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

    @factory.post_generation
    def categories(self, create, extracted, **kwargs):
        if not create or not extracted:
            # Simple build, or nothing to add, do nothing.
            return

        # Add the iterable of categories using bulk addition
        self.categories.add(*extracted)

    created_at = factory.LazyFunction(timezone.now)
    updated_at = factory.LazyFunction(timezone.now)
