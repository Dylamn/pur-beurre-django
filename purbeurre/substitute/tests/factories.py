import factory
from django.utils import timezone
from faker import Faker

from substitute.models import UserSubstitute
from account.tests.factories import UserFactory
from product.tests.factories import ProductFactory

fake = Faker()


class UserSubstituteFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserSubstitute

    user = factory.SubFactory(UserFactory)
    original_product = factory.SubFactory(ProductFactory)
    substitute_product = factory.SubFactory(ProductFactory)

    created_at = factory.LazyFunction(timezone.now)
    updated_at = factory.LazyFunction(timezone.now)
