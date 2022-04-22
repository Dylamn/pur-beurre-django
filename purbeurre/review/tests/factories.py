import factory
from faker import Faker
from django.utils import timezone

from review.models import Review
from account.tests.factories import UserFactory
from product.tests.factories import ProductFactory

fake = Faker()


class ReviewFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Review

    title = fake.words(nb=3)
    content = fake.text()
    rating = fake.random_int(min=1, max=5)

    user = factory.SubFactory(UserFactory)
    product = factory.SubFactory(ProductFactory)

    created_at = factory.LazyFunction(timezone.now)
    updated_at = factory.LazyFunction(timezone.now)
