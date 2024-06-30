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

    def test_get_product(self):
        product = Product.objects.get_product(name='Laptop')
        self.assertIsNotNone(product)
        self.assertEqual(product.stock, 2)

    def test_get_nonexistent_product(self):
        product = Product.objects.get_product(name='Nonexistent')
        self.assertIsNone(product)

    def test_delete_product(self):
        num_of_deleted = Product.objects.delete_product(name='Laptop')
        self.assertEqual(num_of_deleted, (1, {'products.Product': 1}))
        product = Product.objects.get_product(name='Laptop')
        self.assertIsNone(product)

    def test_delete_nonexistent_product(self):
        num_of_deleted = Product.objects.delete_product(name='Nonexistent')
        self.assertIsNone(num_of_deleted)


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

    def test_get_category(self):
        category = Category.objects.get_category(name='Electronics')
        self.assertIsNotNone(category)
        self.assertEqual(category.description, 'Electronic items')

    def test_get_nonexistent_category(self):
        category = Category.objects.get_category(name='Nonexistent')
        self.assertIsNone(category)

    def test_delete_category(self):
        num_of_deleted = Category.objects.delete_category(name='Electronics')
        self.assertEqual(num_of_deleted, (1, {'products.Category': 1}))
        category = Category.objects.get_category(name='Electronics')
        self.assertIsNone(category)

    def test_delete_nonexistent_category(self):
        num_of_deleted = Category.objects.delete_category(name='Nonexistent')
        self.assertIsNone(num_of_deleted)
