

class ProductModelTests(TestCase):
    def test_absolute_url_method(self):
        p = Product(name="Product n°1")

        self.assertTrue(p)
