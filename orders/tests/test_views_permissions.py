from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse

from products.tests.factories import CategoryFactory, ProductFactory, UserFactory
from ecommerce.management.commands.assign_permissions import Command
from products.models import Product, Category
from orders.models import Order, OrderItem
from factories import OrderItemFactory, OrderFactory

import logging

logger = logging.getLogger('django')

'''
access control testing
(checking which view is accessible to each group)
'''

class OrderViewPermissionTest(TestCase):
    """

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
        self.create_url = reverse('order-create')
        self.update_url = reverse('order-update', args=[])
        self.delete_url = reverse('order-delete', args=[])
        self.detail_url = reverse('order-detail', args=[])
        self.list_url = reverse('order-list', args=[])

    # TODO: duplicate move to utils
    def check_permission(self, url, user, expected_status, method='get', data=None):
        """Helper to check permissions for different users and methods."""
        self.client.login(username=user.username, password='password')

        if method == 'post':
            response = self.client.post(url, data=data)
        else:
            response = self.client.get(url)

        self.assertEqual(response.status_code, expected_status)


class OrderItemViewPermissionTest(TestCase):
    """

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
        self.create_url = reverse('orderitem-create')
        self.update_url = reverse('orderitem-update', args=[])
        self.delete_url = reverse('orderitem-delete', args=[])
        self.detail_url = reverse('orderitem-detail', args=[])
        self.list_url = reverse('orderitem-list', args=[])

    # TODO: duplicate move to utils
    def check_permission(self, url, user, expected_status, method='get', data=None):
        """Helper to check permissions for different users and methods."""
        self.client.login(username=user.username, password='password')

        if method == 'post':
            response = self.client.post(url, data=data)
        else:
            response = self.client.get(url)

        self.assertEqual(response.status_code, expected_status)