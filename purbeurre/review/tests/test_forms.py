from django.test import TestCase

from account.tests.factories import UserFactory
from product.tests.factories import ProductFactory
from review.forms import CreateReviewForm
from review.models import Review
from .factories import ReviewFactory


class FormsTests(TestCase):
    def setUp(self) -> None:
        self.user = UserFactory()
        self.product = ProductFactory()
        self.review = ReviewFactory(title='setUp review', user=self.user, product=self.product)

    @staticmethod
    def _reviewExists(data) -> bool:
        return Review.objects.filter(**data).exists()

    def assertReviewExists(self, review_data: dict) -> None:
        self.assertTrue(self._reviewExists(review_data))

    def assertReviewNotExists(self, review_data: dict) -> None:
        self.assertFalse(self._reviewExists(review_data))

    def test_review_creation_validation(self) -> None:
        review_data = {
            'title': "I'm the title",
            'content': "I'm the content.",
            'rating': 5
        }

        self.assertReviewNotExists(review_data)
        form = CreateReviewForm(data=review_data)
        self.assertTrue(form.is_valid())
        form.save(user=self.user, product_id=self.product.id)
        self.assertReviewExists(review_data)

    def test_review_form_with_incorrect_rating_is_not_valid(self) -> None:
        review_data = {
            'title': "I am Justice",
            'content': "Always the content",
            'rating': 10
        }

        self.assertReviewNotExists(review_data)
        form = CreateReviewForm(data=review_data)

        self.assertFalse(form.is_valid())
        self.assertTrue(form.has_error('rating'))

