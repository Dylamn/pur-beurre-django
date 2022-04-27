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
        self.user = UserFactory()
        self.fake_request = HttpRequest()
        self.fake_request.user = self.user

    def test_get_empty_product_reviews(self) -> None:
        a_product = ProductFactory()

        page, user_review = ReviewService.get_product_reviews(request=self.fake_request, product_id=a_product.id)

        self.assertIsInstance(page, Page)
        self.assertEqual(len(page.object_list), 0)
        self.assertEqual(user_review, None)

    def test_get_all_product_reviews_with_a_user_review(self) -> None:
        a_product = ProductFactory()
        a_review = ReviewFactory(user=self.user, product=a_product)
        other_reviews_total = 3
        other_reviews = ReviewFactory.create_batch(size=other_reviews_total, product=a_product)

        self.fake_request.GET.setdefault('page', 1)

        page, user_review = ReviewService.get_product_reviews(request=self.fake_request, product_id=a_product.id)

        self.assertIsInstance(page, Page)
        self.assertIsInstance(user_review, ReviewModel)
        self.assertEqual(len(page.object_list), other_reviews_total)
        self.assertQuerysetEqual(page.object_list, other_reviews)
        self.assertEqual(user_review, a_review)

    def test_should_get_an_empty_user_review(self):
        a_product = ProductFactory()
        reviews_size = 3
        reviews = ReviewFactory.create_batch(size=reviews_size, product=a_product)
        a_review = ReviewFactory(user=self.user)

        page, user_review = ReviewService.get_product_reviews(request=self.fake_request, product_id=a_product.id)

        self.assertIsInstance(page, Page)
        self.assertNotIn(a_review, page.object_list)
        self.assertEqual(len(page.object_list), 3)
        self.assertQuerysetEqual(page.object_list, reviews)
        self.assertEqual(user_review, None)

    def test_get_average_product_reviews_rating(self) -> None:
        a_product = ProductFactory()
        n_3stars_reviews = 3
        n_5stars_reviews = 5
        ReviewFactory.create_batch(size=n_3stars_reviews, rating=3, product=a_product)
        ReviewFactory.create_batch(size=n_5stars_reviews, rating=5, product=a_product)

        estimated_average = round(
            (3 * n_3stars_reviews + 5 * n_5stars_reviews) / (n_3stars_reviews + n_5stars_reviews)
        )
        service_average, _ = ReviewService.get_avg_product_reviews_rating(product_id=a_product.id)

        self.assertEqual(estimated_average, service_average)
