from django.test import TestCase
from products.models import Product, Category
from decimal import Decimal


class ProductManagerTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Electronics', description='Electronic items')
        self.product = Product.objects.create_product(
            name='Laptop',
            description='A powerful laptop',
            price=Decimal(1899.99),
            category=self.category,
            stock=2,
        )

        self.product2 = Product.objects.create_product(
            name='MF',
            description='A mainframe because why not',
            price=Decimal('1'),
            category=self.category,
            stock=500,
        )

    def test_create_product(self):
        self.assertEqual(Product.objects.count(), 2)
        self.assertEqual(self.product.name, 'Laptop')
        self.assertEqual(self.product2.name, 'MF')

    def test_update_product(self):
        updated_product = Product.objects.update_product(self.product, price=899.99)
        self.assertIsNotNone(updated_product)
        self.assertEqual(updated_product.price, Decimal('899.99'))

    # TODO: uncomment when update_product() accepts a product's name and not just a Product object
    # def test_update_nonexistent_product(self):
    #     updated_product = Product.objects.update_product(name='Nonexistent', price=899.99)
    #     self.assertIsNone(updated_product)

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
        with self.assertRaises(Product.DoesNotExist):
            Product.objects.get(name='Laptop')

    def test_delete_nonexistent_product(self):
        num_of_deleted = Product.objects.delete_product(name='Nonexistent')
        self.assertIsNone(num_of_deleted)


class CategoryManagerTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Electronics', description='Electronic items')

    def test_create_category(self):
        self.assertEqual(Category.objects.count(), 1)

    def test_update_category(self):
        updated_category = Category.objects.update_category(name='Electronics', description='something else')
        self.assertIsNotNone(updated_category)
        self.assertEqual(updated_category.description, 'something else')

    def test_update_nonexistent_category(self):
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
