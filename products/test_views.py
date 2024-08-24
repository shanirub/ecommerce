from django.test import TestCase
from django.urls import reverse
from users.models import User
from .models import Product, Category


class ProductViewTests(TestCase):

    def get_product_data(self, product=None, **overrides):
        # TODO: move to separate utils file?
        data = {
            'name': product.name if product else 'Default Name',
            'description': product.description if product else 'Default Description',
            'price': product.price if product else 10.0,
            'stock': product.stock if product else 100,
            'category': product.category.id if product else self.category.id,
        }
        data.update(overrides)
        return data

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

    def test_create_product_success(self):
        self.client.login(username='admin', password='admin')
        product_data = self.get_product_data(self.product, name='snowflake product')
        response = self.client.post(reverse('create_product'), product_data)
        self.assertEqual(response.status_code, 302)  # Check if redirected
        self.assertRedirects(response, reverse('product_list'))
        self.assertTrue(Product.objects.filter(name=self.product.name).exists())  # Check if the product was created

    def test_create_product_invalid_data(self):
        self.client.login(username='admin', password='admin')
        product_data = self.get_product_data(self.product, name='', price='invalid_price', description='something else')
        response = self.client.post(reverse('create_product'), product_data)

        # If redirected, follow the redirect
        if response.status_code == 302:
            response = self.client.get(response.url)

        # Check if form is in the context
        self.assertIn('form', response.context)
        form = response.context['form']
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
        self.assertIn('price', form.errors)

        expected_errors = {
            'name': ['This field is required.'],
            'price': ['Enter a number.']
        }
        self.assertEqual(form.errors, expected_errors)

        # Ensure no product was created with invalid data
        self.assertFalse(Product.objects.filter(name='').exists())
        self.assertFalse(Product.objects.filter(description='something else').exists())

    def test_update_product_invalid_data(self):
        self.client.login(username='admin', password='admin')
        product_data = self.get_product_data(self.product, description='', price='invalid_price',
                                             category='New Category')
        response = self.client.post(reverse('update_product', args=[self.product.pk]), product_data)

        # If redirected, follow the redirect
        if response.status_code == 302:
            response = self.client.get(response.url)

        self.assertEqual(response.status_code, 200)  # Check that it did not redirect

        # Check if form is in the context
        self.assertIn('form', response.context)
        form = response.context['form']

        self.assertTrue(form.errors)

        form = response.context['form']
        self.assertFalse(form.is_valid())
        self.assertIn('category', form.errors)
        self.assertIn('price', form.errors)

