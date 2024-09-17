import factory
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import Group
from products.tests.factories import UserFactory, GroupFactory, ProductFactory, CategoryFactory
from ecommerce.management.commands.assign_permissions import Command

import logging

logger = logging.getLogger('django')


class ProductViewPermissionTest(TestCase):
    def setUp(self):
        # Set up permissions using your custom management command
        Command().handle()

        # Create product and category
        self.category = CategoryFactory(name='cat', description='Sample category')
        self.product = ProductFactory(category=self.category)

        # Fetch existing groups created by Command().handle()
        staff_group = Group.objects.get(name='staff')
        stock_group = Group.objects.get(name='stock_personnel')
        shift_manager_group = Group.objects.get(name='shift_manager')
        customer_group = Group.objects.get(name='customers')

        # Create users and assign existing groups
        self.staff_user = UserFactory(groups=[staff_group])
        self.stock_user = UserFactory(groups=[stock_group])
        self.shift_manager_user = UserFactory(groups=[shift_manager_group])
        self.customer_user = UserFactory(groups=[customer_group])

        # URLs for testing
        self.update_url = reverse('update_product', args=[self.product.pk])
        self.create_url = reverse('create_product')
        self.delete_url = reverse('delete_product', args=[self.product.pk])
        self.detail_url = reverse('product_detail', args=[self.product.pk])

    def check_permission(self, url, user, expected_status, method='get', data=None):
        """Helper to check permissions for different users and methods."""
        self.client.login(username=user.username, password='password')

        if method == 'post':
            response = self.client.post(url, data=data)
        else:
            response = self.client.get(url)

        self.assertEqual(response.status_code, expected_status)

    def test_product_update_permissions(self):
        # Define test cases for GET and POST requests
        test_cases = [
            {'user': self.staff_user, 'expected_status': 200, 'method': 'get'},
            {'user': self.stock_user, 'expected_status': 200, 'method': 'get'},
            {'user': self.shift_manager_user, 'expected_status': 200, 'method': 'get'},
            {'user': self.customer_user, 'expected_status': 403, 'method': 'get'},

            {'user': self.staff_user, 'expected_status': 200, 'method': 'post', 'data': factory.build(dict, FACTORY_CLASS=ProductFactory)},
            {'user': self.stock_user, 'expected_status': 200, 'method': 'post', 'data': factory.build(dict, FACTORY_CLASS=ProductFactory)},
            {'user': self.shift_manager_user, 'expected_status': 200, 'method': 'post',
             'data': factory.build(dict, FACTORY_CLASS=ProductFactory)},
            {'user': self.customer_user, 'expected_status': 403, 'method': 'post',
             'data': factory.build(dict, FACTORY_CLASS=ProductFactory)},

        ]

        for case in test_cases:
            with self.subTest(user=case['user'].username, method=case['method']):
                logger.info(f"*** testing product UPDATE for case: {case} \n")
                self.check_permission(self.update_url, case['user'], case['expected_status'], method=case['method'], data=case.get('data'))

    def test_product_create_permissions(self):
        # Define test cases for product creation permissions
        test_cases = [
            {'user': self.staff_user, 'expected_status': 200, 'method': 'get'},
            {'user': self.customer_user, 'expected_status': 403, 'method': 'get'},
            {'user': self.stock_user, 'expected_status': 403, 'method': 'get'},
            {'user': self.shift_manager_user, 'expected_status': 200, 'method': 'get'},

            {'user': self.staff_user, 'expected_status': 200, 'method': 'post', 'data': factory.build(dict, FACTORY_CLASS=ProductFactory)},
            {'user': self.customer_user, 'expected_status': 403, 'method': 'post', 'data': factory.build(dict, FACTORY_CLASS=ProductFactory)},
            {'user': self.stock_user, 'expected_status': 403, 'method': 'post', 'data': factory.build(dict, FACTORY_CLASS=ProductFactory)},
            {'user': self.shift_manager_user, 'expected_status': 200, 'method': 'post', 'data': factory.build(dict, FACTORY_CLASS=ProductFactory)},

        ]

        for case in test_cases:
            with self.subTest(user=case['user'].username, method=case['method']):
                logger.info(f"*** testing product CREATE for case: {case} \n")
                self.check_permission(self.create_url, case['user'], case['expected_status'], method=case['method'], data=case.get('data'))

        def test_product_delete_permissions(self):
            pass

        def test_product_view_permissions(self):
            pass
