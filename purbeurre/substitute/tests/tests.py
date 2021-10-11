from django.test import TestCase
from django.shortcuts import reverse

from account.tests.factories import UserFactory


# Create your tests here.
class UserSubstituteListViewTests(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        """Load initial data for the TestCase."""
        cls.url = reverse('substitute:index')

    def setUp(self) -> None:
        self.user = UserFactory()
        self.client.force_login(self.user)

    def test_user_substitute_list_template(self) -> None:
        response = self.client.get(self.url)

        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, template_name='substitute/index.html')
