from django.test import TestCase
from .models import Product, Category


class ProductManagerTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Electronics', description='Electronic items')
        self.product = Product.objects.create_product(
            name='Laptop',
            description='A powerful laptop',
            price=999.99,
            category=self.category,
            stock=2,
        )

    def test_create_product(self):
        self.assertEqual(Product.objects.count(), 1)
        self.assertEqual(self.product.name, 'Laptop')

    def test_update_product(self):
        updated_product = Product.objects.update_product(name='Laptop', price=899.99)
        self.assertIsNotNone(updated_product)
        self.assertEqual(updated_product.price, 899.99)

    def test_update_nonexistent_product(self):
        updated_product = Product.objects.update_product(name='Nonexistent', price=899.99)
        self.assertIsNone(updated_product)


class CategoryManagerTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Electronics', description='Electronic items')

    def test_create_category(self):
        self.assertEqual(Category.objects.count(), 1)

    def test_update_product(self):
        updated_category = Category.objects.update_category(name='Electronics', description='something else')
        self.assertIsNotNone(updated_category)
        self.assertEqual(updated_category.description, 'something else')

    def test_update_nonexistent_product(self):
        updated_category = Category.objects.update_category(name='Nonexistent', description='something else')
        self.assertIsNone(updated_category)
