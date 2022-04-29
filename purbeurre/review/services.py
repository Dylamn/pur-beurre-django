from typing import Union

from django.core.paginator import Paginator, Page
from django.db.models import Avg
from django.http import HttpRequest

from review.models import Review


class ReviewService:
    @staticmethod
    def get_product_reviews(*, request: HttpRequest, product_id: int, per_page: int = 6) -> [Page, Union[Review, None]]:
        """Get all reviews of the specified product. Pagination is applied"""
        user_review = None
        page_number = request.GET.get('page', 1)

        if request.user.is_authenticated:
            user_review = Review.objects.filter(user=request.user, product_id=product_id).first()

        review_list = Review.objects.filter(product_id=product_id)
        if user_review:
            review_list = review_list.exclude(user=request.user)

        paginator = Paginator(review_list, per_page=per_page)
        page = paginator.get_page(page_number)

        return page, user_review

    @staticmethod
    def get_avg_product_reviews_rating(*, product_id) -> [int, int]:
        """Get the average reviews rating of the specified product"""
        query = Review.objects.filter(product_id=product_id)
        total_reviews = len(query)
        avg = query.aggregate(Avg('rating')).get('rating__avg')

        return round(avg or 0), total_reviews
