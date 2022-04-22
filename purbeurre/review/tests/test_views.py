from django.test import TestCase
from django.shortcuts import reverse

from .factories import ReviewFactory


class ReviewViewsTests(TestCase):
    def test_get_an_existing_review(self):
        a_review = ReviewFactory()
        url = reverse('review:review', args=(a_review.id,))
        response = self.client.get(url)

        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, template_name='review/edit.html')
