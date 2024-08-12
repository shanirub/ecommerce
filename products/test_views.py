from django.test import TestCase
from django.urls import reverse
from users.models import User
from .models import Product, Category


class ProductViewTests(TestCase):

    def setUp(self):
        self.admin_user = User.objects.create_superuser(username='admin', password='admin', email='admin@example.com')
        self.category = Category.objects.create_category(name='cat1', description='cat example')
        self.product = Product.objects.create(
            name='Test Product',
            description='Test Description',
            price=10.0,
            stock=100,
            category=self.category
        )

    def test_update_product_view(self):
        self.client.login(username='admin', password='admin')
        response = self.client.get(reverse('update_product', kwargs={'pk': self.product.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'update_product.html')

    def test_create_product_view(self):
        self.client.login(username='admin', password='admin')
        response = self.client.get(reverse('create_product'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_product.html')
