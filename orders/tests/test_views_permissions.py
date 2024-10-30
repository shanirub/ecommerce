from django.contrib.auth.models import Group
from django.contrib.messages import debug, warning
from django.test import TestCase
from django.urls import reverse

from products.tests.factories import CategoryFactory, ProductFactory, UserFactory
from orders.tests.factories import OrderItemFactory, OrderFactory
from ecommerce.management.commands.assign_permissions import Command
from ecommerce.utils import check_permission
import factory


import logging

logger = logging.getLogger('django')

'''
access control testing
(checking which view is accessible to each group)
'''


class OrderViewPermissionTest(TestCase):
    """
    Test permissions for different user groups in the order views.

    Quick reference to HTTP response status codes used in tests:
    200 - OK
    302 - Redirect
    403 - Forbidden (doesn't have required permission)
    404 - Not found (has permission but resource is missing)
    """

    def setUp(self):
        # Set up permissions using the assign_permissions script
        Command().handle()

        # Create orders for two different customers
        self.order_customer1 = OrderFactory()
        self.order_customer2 = OrderFactory()
        self.order_item1 = OrderItemFactory(order=self.order_customer1)
        self.order_item2 = OrderItemFactory(order=self.order_customer2)

        # Fetch existing groups created by Command().handle()
        staff_group = Group.objects.get(name='staff')
        shift_manager_group = Group.objects.get(name='shift_manager')
        customer_group = Group.objects.get(name='customers')
        stock_group = Group.objects.get(name='stock_personnel')

        # Create users and assign them to groups
        self.staff_user = UserFactory(groups=[staff_group])
        self.shift_manager_user = UserFactory(groups=[shift_manager_group])
        self.customer1_user = UserFactory(groups=[customer_group])
        logger.warning(f"self.customer1_user= {self.customer1_user}")
        self.customer2_user = UserFactory(groups=[customer_group])
        logger.warning(f"self.customer2_user= {self.customer2_user}")

        self.stock_personnel_user = UserFactory(groups=[stock_group])

        # Assign the first order to customer1 and the second order to customer2
        self.order_customer1.user = self.customer1_user
        self.order_customer1.save()

        self.order_customer2.user = self.customer2_user
        self.order_customer2.save()

        # dicts for both customers to use in update
        self.order_customer1_data = factory.build(dict, FACTORY_CLASS=OrderFactory)
        self.order_customer1_data['user'] = self.customer1_user

        self.order_customer2_data = factory.build(dict, FACTORY_CLASS=OrderFactory)
        self.order_customer2_data['user'] = self.customer2_user

        # URLs for testing
        self.update_order_url1 = reverse('order-update', args=[self.order_customer1.pk])
        self.update_order_url2 = reverse('order-update', args=[self.order_customer2.pk])
        self.create_order_url = reverse('order-create')
        self.delete_order_url = reverse('order-delete', args=[self.order_customer1.pk])
        self.detail_order_url1 = reverse('order-detail', args=[self.order_customer1.pk])
        self.list_order_url = reverse('order-list')

    def test_order_list_permissions(self):
        """ Test permissions for viewing the order list. """
        test_cases = [
            {'user': self.staff_user, 'expected_status': 200, 'method': 'get'},
            {'user': self.shift_manager_user, 'expected_status': 200, 'method': 'get'},
            # Shift managers can view orders
            {'user': self.customer1_user, 'expected_status': 200, 'method': 'get'},
            {'user': self.stock_personnel_user, 'expected_status': 403, 'method': 'get'},
            # only Stock personnel cannot view orders
        ]

        for case in test_cases:
            with self.subTest(user=case['user'].username, method=case['method']):
                check_permission(self, self.list_order_url, case['user'], case['expected_status'],
                                 method=case['method'])

    def test_order_update_permissions(self):
        """ Test permissions for updating orders. """
        test_cases = [
            {'user': self.staff_user, 'expected_status': 403, 'method': 'get'},
            {'user': self.shift_manager_user, 'expected_status': 200, 'method': 'get'},
            {'user': self.customer1_user, 'expected_status': 200, 'method': 'get'},
            # Customer1 can update their own order
            {'user': self.customer2_user, 'expected_status': 403, 'method': 'get'},
            # Customer2 cannot update Customer1's order
            {'user': self.stock_personnel_user, 'expected_status': 403, 'method': 'get'},
            # Stock personnel cannot update orders

            # Test POST requests (updating orders)
            {'user': self.staff_user, 'expected_status': 403, 'method': 'post',
             'data': factory.build(dict, FACTORY_CLASS=OrderFactory)},
            {'user': self.shift_manager_user, 'expected_status': 302, 'method': 'post',
             'data': factory.build(dict, FACTORY_CLASS=OrderFactory)},
            {'user': self.customer1_user, 'expected_status': 302, 'method': 'post',
             'data': self.order_customer1_data},
            {'user': self.customer2_user, 'expected_status': 403, 'method': 'post',
             'data': self.order_customer1_data},  # Cannot update another customer's order
            {'user': self.stock_personnel_user, 'expected_status': 403, 'method': 'post',
             'data': factory.build(dict, FACTORY_CLASS=OrderFactory)},  # Stock personnel cannot update orders
        ]

        for case in test_cases:
            url = self.update_order_url1 # if case['user'] == self.customer1_user else self.update_order_url2
            with self.subTest(user=case['user'].username, method=case['method']):
                data = case.get('data')
                logger.warning(f"** data= {data} \n url= {url}\n user= {case['user']}")
                check_permission(self, url, case['user'], case['expected_status'], method=case['method'],
                                 data=case.get('data'))

    def test_order_create_permissions(self):
        """ Test permissions for creating orders. """
        test_cases = [
            {'user': self.staff_user, 'expected_status': 403, 'method': 'get'},  # Staff cannot create orders
            {'user': self.shift_manager_user, 'expected_status': 200, 'method': 'get'},
            # Shift manager can create orders
            {'user': self.customer1_user, 'expected_status': 200, 'method': 'get'},  # Customers can create orders
            {'user': self.stock_personnel_user, 'expected_status': 403, 'method': 'get'},
            # Stock personnel cannot create orders

            # Test POST requests (creating orders)
            {'user': self.staff_user, 'expected_status': 403, 'method': 'post',
             'data': factory.build(dict, FACTORY_CLASS=OrderFactory)},
            {'user': self.shift_manager_user, 'expected_status': 302, 'method': 'post',
             'data': factory.build(dict, FACTORY_CLASS=OrderFactory)},
            {'user': self.customer1_user, 'expected_status': 302, 'method': 'post',
             'data': factory.build(dict, FACTORY_CLASS=OrderFactory)},
            {'user': self.stock_personnel_user, 'expected_status': 403, 'method': 'post',
             'data': factory.build(dict, FACTORY_CLASS=OrderFactory)},
        ]

        for case in test_cases:
            with self.subTest(user=case['user'].username, method=case['method']):
                check_permission(self, self.create_order_url, case['user'], case['expected_status'],
                                 method=case['method'], data=case.get('data'))

    def test_order_delete_permissions(self):
        """ Test permissions for deleting orders. """
        test_cases = [
            {'user': self.staff_user, 'expected_status': 403, 'method': 'get'},  # Staff cannot delete orders
            {'user': self.shift_manager_user, 'expected_status': 200, 'method': 'get'},
            # Shift manager can delete orders
            {'user': self.customer1_user, 'expected_status': 200, 'method': 'get'},
            # Customer can delete their own order
            {'user': self.customer2_user, 'expected_status': 403, 'method': 'get'},
            # Customer cannot delete another customer's order
            {'user': self.stock_personnel_user, 'expected_status': 403, 'method': 'get'},
            # Stock personnel cannot delete orders

            # Test POST requests (deleting orders)
            {'user': self.staff_user, 'expected_status': 403, 'method': 'post'},
            {'user': self.shift_manager_user, 'expected_status': 302, 'method': 'post'},
            {'user': self.customer1_user, 'expected_status': 403, 'method': 'post'},
            {'user': self.customer2_user, 'expected_status': 403, 'method': 'post'},
            {'user': self.stock_personnel_user, 'expected_status': 403, 'method': 'post'},
        ]

        for case in test_cases:
            with self.subTest(user=case['user'].username, method=case['method']):
                check_permission(self, self.delete_order_url, case['user'], case['expected_status'],
                                 method=case['method'])

    def test_order_delete_permissions_for_customers(self):
        """ Testing user can only delete its own orders """
        test_cases = [
            {'user': self.customer2_user, 'expected_status': 403, 'method': 'post'},
            {'user': self.customer1_user, 'expected_status': 302, 'method': 'post'},
        ]

        for case in test_cases:
            with self.subTest(user=case['user'].username, method=case['method']):
                check_permission(self, self.delete_order_url, case['user'], case['expected_status'],
                                 method=case['method'])

    def test_order_detail_permissions(self):
        """ Test permissions for viewing order details. """
        test_cases = [
            {'user': self.staff_user, 'expected_status': 200, 'method': 'get'},  # Staff can view orders
            {'user': self.shift_manager_user, 'expected_status': 200, 'method': 'get'},  # Shift manager can view orders
            {'user': self.customer1_user, 'expected_status': 200, 'method': 'get'},  # customer can view its own order
            {'user': self.customer2_user, 'expected_status': 403, 'method': 'get'}, # customer cannot view other's order
            # Customer cannot view another customer's order
            {'user': self.stock_personnel_user, 'expected_status': 403, 'method': 'get'},
            # Stock personnel cannot view orders
        ]

        for case in test_cases:
            url = self.detail_order_url1
            with self.subTest(user=case['user'].username, method=case['method']):
                check_permission(self, url, case['user'], case['expected_status'], method=case['method'])


class OrderItemViewPermissionTest(TestCase):
    """
    Test permissions for different user groups in the OrderItem views.

    Quick reference to HTTP response status codes used in tests:
    200 - OK
    302 - Redirect
    403 - Forbidden (doesn't have required permission)
    404 - Not found (has permission but resource is missing)
    """

    def setUp(self):
        self._fixture_teardown()
        self._fixture_setup()

        # Set up permissions using the assign_permissions script
        Command().handle()

        # Create orders for two different customers
        self.order_customer1 = OrderFactory()
        self.order_customer2 = OrderFactory()
        self.order_item1 = OrderItemFactory(order=self.order_customer1)
        self.order_item2 = OrderItemFactory(order=self.order_customer2)

        # Fetch existing groups created by Command().handle()
        staff_group = Group.objects.get(name='staff')
        shift_manager_group = Group.objects.get(name='shift_manager')
        customer_group = Group.objects.get(name='customers')
        stock_group = Group.objects.get(name='stock_personnel')

        # Create users and assign them to groups
        self.staff_user = UserFactory(groups=[staff_group])
        self.shift_manager_user = UserFactory(groups=[shift_manager_group])
        self.customer1_user = UserFactory(groups=[customer_group])
        self.customer2_user = UserFactory(groups=[customer_group])
        print(f"1 {self.customer1_user}\n 2 {self.customer2_user}")
        self.stock_personnel_user = UserFactory(groups=[stock_group])

        # Assign the first order to customer1 and the second order to customer2
        self.order_customer1.user = self.customer1_user
        self.order_customer1.save()

        self.order_customer2.user = self.customer2_user
        self.order_customer2.save()

        # URLs for testing
        self.create_order_item_url1 = reverse('orderitem-create', args=[self.order_customer1.pk])
        self.create_order_item_url2 = reverse('orderitem-create', args=[self.order_customer2.pk])
        self.update_order_item_url1 = reverse('orderitem-update', args=[self.order_item1.pk])
        self.update_order_item_url2 = reverse('orderitem-update', args=[self.order_item2.pk])
        self.delete_order_item_url1 = reverse('orderitem-delete', args=[self.order_item1.pk])
        self.detail_order_item_url1 = reverse('orderitem-detail', args=[self.order_item1.pk])
        # self.list_order_item_url1 = reverse('orderitem-list', args=[])

    # TODO: view and urls currently not used
    # def test_orderitem_list_permissions(self):
    #     """ Test permissions for viewing the order item list. """
    #     test_cases = [
    #         {'user': self.customer1_user, 'expected_status': 200, 'method': 'get'},
    #         {'user': self.shift_manager_user, 'expected_status': 200, 'method': 'get'},
    #         {'user': self.staff_user, 'expected_status': 403, 'method': 'get'},
    #         {'user': self.stock_personnel_user, 'expected_status': 403, 'method': 'get'},
    #     ]
    #
    #     for case in test_cases:
    #         with self.subTest(user=case['user'].username, method=case['method']):
    #             check_permission(self, self.list_order_item_url1, case['user'], case['expected_status'],
    #                              method=case['method'])

    def test_orderitem_create_permissions(self):
        """ Test permissions for creating an order item. """
        test_cases = [
            {'user': self.customer1_user, 'expected_status': 200, 'method': 'get', 'data':None},
            {'user': self.customer2_user, 'expected_status': 403, 'method': 'get', 'data':None},
            {'user': self.shift_manager_user, 'expected_status': 200, 'method': 'get', 'data':None},
            {'user': self.staff_user, 'expected_status': 403, 'method': 'get', 'data':None},

            {'user': self.customer1_user, 'expected_status': 302, 'method': 'post', 'data': {'product': 1, 'quantity': 2, 'price': 10}},
            {'user': self.customer2_user, 'expected_status': 403, 'method': 'post', 'data': {'product': 1, 'quantity': 2, 'price': 10}},
            {'user': self.shift_manager_user, 'expected_status': 302, 'method': 'post', 'data': {'product': 1, 'quantity': 2, 'price': 10}},
            {'user': self.stock_personnel_user, 'expected_status': 403, 'method': 'post', 'data': {'product': 1, 'quantity': 2, 'price': 10}},
            {'user': self.staff_user, 'expected_status': 403, 'method': 'post',
             'data': {'product': 1, 'quantity': 2, 'price': 10}},
        ]

        for case in test_cases:
            with self.subTest(user=case['user'].username, method=case['method']):
                check_permission(self, self.create_order_item_url1, case['user'], case['expected_status'],
                                 method=case['method'], data=case['data'])

    def test_orderitem_update_permissions(self):
        """ Test permissions for updating an order item. """
        test_cases = [
            {'user': self.customer1_user, 'expected_status': 302, 'method': 'post', 'data': {'quantity': 5, 'price': 12}},
            {'user': self.customer2_user, 'expected_status': 403, 'method': 'post', 'data': {'quantity': 5, 'price': 12}},
            {'user': self.shift_manager_user, 'expected_status': 302, 'method': 'post', 'data': {'quantity': 5, 'price': 12}},
            {'user': self.staff_user, 'expected_status': 403, 'method': 'post', 'data': {'quantity': 5, 'price': 12}},
        ]

        for case in test_cases:
            with self.subTest(user=case['user'].username, method=case['method']):
                check_permission(self, self.update_order_item_url1, case['user'], case['expected_status'],
                                 method=case['method'], data=case['data'])

    def test_orderitem_delete_permissions(self):
        """ Test permissions for deleting an order item. """
        test_cases = [
            {'user': self.customer1_user, 'expected_status': 302, 'method': 'post'},
            {'user': self.customer2_user, 'expected_status': 403, 'method': 'post'},
            # shift manager has permissions, but item was already deleted by customer1
            {'user': self.shift_manager_user, 'expected_status': 403, 'method': 'post'},
            {'user': self.staff_user, 'expected_status': 403, 'method': 'post'},
        ]

        for case in test_cases:
            with self.subTest(user=case['user'].username, method=case['method']):
                check_permission(self, self.delete_order_item_url1, case['user'], case['expected_status'],
                                 method=case['method'])

    def test_orderitem_delete_permissions_shift_manager(self):
        """ supplementary test, just to show shift manager can delete items created by customers """
        test_cases = [
            {'user': self.shift_manager_user, 'expected_status': 302, 'method': 'post'},
        ]


    def test_orderitem_detail_permissions(self):
        """ Test permissions for viewing order item details. """
        test_cases = [
            {'user': self.customer1_user, 'expected_status': 200, 'method': 'get'},
            {'user': self.customer2_user, 'expected_status': 403, 'method': 'get'},
            {'user': self.shift_manager_user, 'expected_status': 200, 'method': 'get'},
            {'user': self.staff_user, 'expected_status': 200, 'method': 'get'},
        ]

        for case in test_cases:
            with self.subTest(user=case['user'].username, method=case['method']):
                check_permission(self, self.detail_order_item_url1, case['user'], case['expected_status'],
                                 method=case['method'])

