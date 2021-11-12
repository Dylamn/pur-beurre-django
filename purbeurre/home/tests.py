from django.test import TestCase


# Create your tests here.
class HomeViewsTests(TestCase):
    def test_index_template_url(self):
        response = self.client.get('/')

        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, template_name='home/index.html')

    def test_terms_template_url(self):
        response = self.client.get('/terms/')

        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, template_name='home/terms.html')
