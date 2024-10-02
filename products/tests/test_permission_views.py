import factory
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import Group
from products.tests.factories import UserFactory, GroupFactory, ProductFactory, CategoryFactory
from ecommerce.management.commands.assign_permissions import Command

import logging

logger = logging.getLogger('django')


class ProductViewPermissionTest(TestCase):
    """
    test views permissions

    the functionality of views is tested in test_views.py

    quick reference to http response status codes used in tests:
    200 - ok
    302 - redirect
    403 - couldn't access (doesn't have permission required)
    404 - couldn't access (has permission, but resource is missing)
    """
    def setUp(self):
        # Set up permissions using assign_permissions script
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
        test_cases = [
            {'user': self.staff_user, 'expected_status': 200, 'method': 'get'},
            {'user': self.customer_user, 'expected_status': 403, 'method': 'get'},
            {'user': self.stock_user, 'expected_status': 403, 'method': 'get'},
            {'user': self.shift_manager_user, 'expected_status': 200, 'method': 'get'},

            # successful delete - redirect (302) to product_list
            {'user': self.shift_manager_user, 'expected_status': 302, 'method': 'post',
             'data': factory.build(dict, FACTORY_CLASS=ProductFactory)},
            {'user': self.customer_user, 'expected_status': 403, 'method': 'post',
             'data': factory.build(dict, FACTORY_CLASS=ProductFactory)},
            {'user': self.stock_user, 'expected_status': 403, 'method': 'post',
             'data': factory.build(dict, FACTORY_CLASS=ProductFactory)},

            # since product was successfully deleted by shift_manager_user,
            # 404 is expected (has permission, but resource is missing)
            {'user': self.staff_user, 'expected_status': 404, 'method': 'post',
             'data': factory.build(dict, FACTORY_CLASS=ProductFactory)},
        ]

        for case in test_cases:
            with self.subTest(user=case['user'].username, method=case['method']):
                logger.info(f"*** testing product DELETE for case: {case} \n")
                self.check_permission(self.delete_url, case['user'], case['expected_status'], method=case['method'],
                                      data=case.get('data'))

    def test_product_detail_permissions(self):
        test_cases = [
            {'user': self.staff_user, 'expected_status': 200, 'method': 'get'},
            {'user': self.customer_user, 'expected_status': 200, 'method': 'get'},
            {'user': self.stock_user, 'expected_status': 200, 'method': 'get'},
            {'user': self.shift_manager_user, 'expected_status': 200, 'method': 'get'},
        ]

        for case in test_cases:
            with self.subTest(user=case['user'].username, method=case['method']):
                logger.info(f"*** testing product DETAIL for case: {case} \n")
                self.check_permission(self.detail_url, case['user'], case['expected_status'], method=case['method'],
                                      data=case.get('data'))


class CategoryViewPermissionsTest(TestCase):
    def setUp(self):
        # Set up permissions using assign_permissions script
        Command().handle()

        # Fetch existing groups created by Command().handle()
        stock_group = Group.objects.get(name='stock_personnel')
        shift_manager_group = Group.objects.get(name='shift_manager')
        customer_group = Group.objects.get(name='customers')
        staff_group = Group.objects.get(name='staff')

        # Create users and assign existing groups
        self.staff_user = UserFactory(groups=[staff_group])
        self.stock_user = UserFactory(groups=[stock_group])
        self.shift_manager_user = UserFactory(groups=[shift_manager_group])
        self.customer_user = UserFactory(groups=[customer_group])
        self.category = CategoryFactory(name='cat', description='Sample category')

        # URLs for testing
        self.create_url = reverse('create_category')
        self.update_url = reverse('update_category', args=[self.category.pk])
        self.delete_url = reverse('delete_category', args=[self.category.pk])
        self.detail_url = reverse('category_detail', args=[self.category.pk])

    # TODO: duplicate move to utils
    def check_permission(self, url, user, expected_status, method='get', data=None):
        """Helper to check permissions for different users and methods."""
        self.client.login(username=user.username, password='password')

        if method == 'post':
            response = self.client.post(url, data=data)
        else:
            response = self.client.get(url)

        self.assertEqual(response.status_code, expected_status)

    def test_category_create_permissions(self):
        test_cases = [
            {'user': self.staff_user, 'expected_status': 200, 'method': 'get'},
            {'user': self.shift_manager_user, 'expected_status': 200, 'method': 'get'},
            {'user': self.customer_user, 'expected_status': 403, 'method': 'get'},
            {'user': self.stock_user, 'expected_status': 403, 'method': 'get'},

            {'user': self.staff_user, 'expected_status': 302, 'method': 'post',
             'data': factory.build(dict, FACTORY_CLASS=CategoryFactory)},
            {'user': self.shift_manager_user, 'expected_status': 302, 'method': 'post',
             'data': factory.build(dict, FACTORY_CLASS=CategoryFactory)},
            {'user': self.customer_user, 'expected_status': 403, 'method': 'post',
             'data': factory.build(dict, FACTORY_CLASS=CategoryFactory)},
            {'user': self.stock_user, 'expected_status': 403, 'method': 'post',
             'data': factory.build(dict, FACTORY_CLASS=CategoryFactory)},

        ]

        for case in test_cases:
            with self.subTest(user=case['user'].username, method=case['method']):
                logger.info(f"*** testing product CREATE for case: {case} \n")
                self.check_permission(self.create_url, case['user'], case['expected_status'], method=case['method'],
                                      data=case.get('data'))

    def test_category_update_permissions(self):
        test_cases = [
            {'user': self.staff_user, 'expected_status': 200, 'method': 'get'},
            {'user': self.shift_manager_user, 'expected_status': 200, 'method': 'get'},
            {'user': self.customer_user, 'expected_status': 403, 'method': 'get'},
            {'user': self.stock_user, 'expected_status': 403, 'method': 'get'},

            {'user': self.staff_user, 'expected_status': 302, 'method': 'post',
             'data': factory.build(dict, FACTORY_CLASS=CategoryFactory)},
            {'user': self.shift_manager_user, 'expected_status': 302, 'method': 'post',
             'data': factory.build(dict, FACTORY_CLASS=CategoryFactory)},
            {'user': self.customer_user, 'expected_status': 403, 'method': 'post',
             'data': factory.build(dict, FACTORY_CLASS=CategoryFactory)},
            {'user': self.stock_user, 'expected_status': 403, 'method': 'post',
             'data': factory.build(dict, FACTORY_CLASS=CategoryFactory)},

        ]

        for case in test_cases:
            with self.subTest(user=case['user'].username, method=case['method']):
                logger.info(f"*** testing product UPDATE for case: {case} \n")
                self.check_permission(self.update_url, case['user'], case['expected_status'], method=case['method'],
                                      data=case.get('data'))

    def test_category_delete_permissions(self):
        test_cases = [
            {'user': self.staff_user, 'expected_status': 200, 'method': 'get'},
            {'user': self.shift_manager_user, 'expected_status': 200, 'method': 'get'},
            {'user': self.customer_user, 'expected_status': 403, 'method': 'get'},
            {'user': self.stock_user, 'expected_status': 403, 'method': 'get'},

            {'user': self.staff_user, 'expected_status': 302, 'method': 'post'},
            {'user': self.shift_manager_user, 'expected_status': 404, 'method': 'post'},
            {'user': self.customer_user, 'expected_status': 403, 'method': 'post'},
            {'user': self.stock_user, 'expected_status': 403, 'method': 'post'},
        ]

        for case in test_cases:
            with self.subTest(user=case['user'].username, method=case['method']):
                logger.info(f"*** testing product DELETE for case: {case} \n")
                self.check_permission(self.delete_url, case['user'], case['expected_status'], method=case['method'])

    def test_category_detail_permissions(self):
        test_cases = [
            {'user': self.staff_user, 'expected_status': 200, 'method': 'get'},
            {'user': self.shift_manager_user, 'expected_status': 200, 'method': 'get'},
            {'user': self.customer_user, 'expected_status': 200, 'method': 'get'},
            {'user': self.stock_user, 'expected_status': 200, 'method': 'get'},
        ]

        for case in test_cases:
            with self.subTest(user=case['user'].username, method=case['method']):
                logger.info(f"*** testing product DETAIL for case: {case} \n")
                self.check_permission(self.detail_url, case['user'], case['expected_status'], method=case['method'])
