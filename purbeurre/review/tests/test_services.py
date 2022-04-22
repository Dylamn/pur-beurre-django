from math import floor

from django.core.paginator import Page
from django.test import TestCase
from django.http import HttpRequest

from product.tests.factories import ProductFactory
from review.models import Review as ReviewModel
from review.services import ReviewService
from account.tests.factories import UserFactory
from review.tests.factories import ReviewFactory


class ReviewServiceTests(TestCase):
    def setUp(self) -> None:
        self.fake_request = HttpRequest()

    def test_get_all_product_reviews(self):
        """Tests"""
        user = UserFactory()
        a_product = ProductFactory()
        a_review = ReviewFactory(user=user, product=a_product)
        another_review = ReviewFactory(product=a_product)

        self.fake_request.user = user
        self.fake_request.GET.setdefault('page', 1)

        page, user_review = ReviewService.get_product_reviews(request=self.fake_request, product_id=a_product.id)

        self.assertIsInstance(page, Page)
        self.assertIsInstance(user_review, ReviewModel)
        self.assertEqual(1, len(page.object_list))
        self.assertEqual(page.object_list[0], another_review)
        self.assertEqual(user_review, a_review)

    def test_get_average_product_reviews_rating(self):
        a_product = ProductFactory()
        stars3_reviews = ReviewFactory.create_batch(size=3, rating=3, product=a_product)
        stars5_reviews = ReviewFactory.create_batch(size=2, rating=5, product=a_product)

        estimated_average = floor((3 * 3 + 5 * 2) / 5)
        service_average, _ = ReviewService.get_avg_product_reviews_rating(product_id=a_product.id)

        self.assertEqual(estimated_average, service_average)
