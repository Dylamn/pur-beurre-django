import factory
from faker import Faker
from django.utils import timezone
from django.contrib.auth.models import Group

from account.models import User

fake = Faker()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = fake.unique.name()
    email = fake.unique.ascii_safe_email()
    first_name = fake.first_name()
    last_name = fake.last_name()
    password = factory.PostGenerationMethodCall('set_password', '-'.join(fake.words(3)))

    is_staff = False
    is_superuser = False

    last_login = None
    date_joined = factory.LazyFunction(timezone.now)
