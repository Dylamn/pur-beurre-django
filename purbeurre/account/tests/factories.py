import factory
from faker import Faker
from django.utils import timezone

from account.models import User

fake = Faker()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: fake.name() + str(n))
    first_name = fake.first_name()
    last_name = fake.last_name()
    email = factory.LazyAttribute(
        lambda u: "{0}@example.com".format(
            u.username
        ).lower()
    )

    password = factory.PostGenerationMethodCall('set_password', '-'.join(fake.words(3)))

    is_active = True
    is_staff = False
    is_superuser = False

    last_login = None
    date_joined = factory.LazyFunction(timezone.now)
