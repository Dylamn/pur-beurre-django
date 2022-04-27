from django.core.exceptions import ValidationError
from django.test import TestCase

from review.tests.factories import ReviewFactory


class ReviewModelTest(TestCase):
    def setUp(self) -> None:
        self.review = ReviewFactory(rating=5)

    def test_dunder_str_method(self) -> None:
        expected_string = "Review n°" + str(self.review.id) + " (" + self.review.product.name + ")"

        self.assertEqual(str(self.review), expected_string)

    def test_rating_validation(self):
        self.review.rating = 6

        with self.assertRaises(ValidationError):
            self.review.clean_fields()
