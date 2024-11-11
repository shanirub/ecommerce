from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse

from products.tests.factories import UserFactory
from orders.tests.factories import OrderItemFactory, OrderFactory
from ecommerce.management.commands.assign_permissions import Command
from ecommerce.utils import check_permission
from django.forms.models import model_to_dict


import logging

logger = logging.getLogger('django')

'''
access control testing
(checking which view is accessible to each group)
'''

class BaseOrderTestData(TestCase):
    @classmethod
    def setUpTestData(cls):
        ''' runs once for each class '''
        # Set up permissions using the assign_permissions script
        Command().handle()

        # Fetch existing groups created by Command().handle()
        staff_group = Group.objects.get(name='staff')
        shift_manager_group = Group.objects.get(name='shift_manager')
        customer_group = Group.objects.get(name='customers')
        stock_group = Group.objects.get(name='stock_personnel')

        # Create users and assign them to groups
        cls.staff_user = UserFactory(groups=[staff_group])
        cls.shift_manager_user = UserFactory(groups=[shift_manager_group])
        cls.customer1_user = UserFactory(groups=[customer_group])
        logger.warning(f"customer1_user= {cls.customer1_user}, id= {cls.customer1_user.id}")
        cls.customer2_user = UserFactory(groups=[customer_group])
        logger.warning(f"customer2_user= {cls.customer2_user}, id= {cls.customer2_user.id}")
        cls.stock_personnel_user = UserFactory(groups=[stock_group])


    @classmethod
    def setUp(cls):
        ''' runs before each test method '''

        # create orders and order items
        cls.order_customer1 = OrderFactory(user=cls.customer1_user, is_paid=False)
        cls.order_customer2 = OrderFactory(user=cls.customer2_user, is_paid=False)
        cls.order_customer1_order_item = OrderItemFactory(order=cls.order_customer1)
        cls.order_customer2_order_item = OrderItemFactory(order=cls.order_customer2)

        # create dicts based on objects, to be used in update/create tests
        cls.order_customer1_data = model_to_dict(cls.order_customer1)
        cls.order_customer1_data__for_update = {**cls.order_customer1_data, 'is_paid': True}
        cls.order_customer2_data = model_to_dict(cls.order_customer2)
        cls.order_customer2_data__for_update = {**cls.order_customer2_data, 'is_paid': True}

        cls.order_customer1_order_item_data = model_to_dict(cls.order_customer1_order_item)
        cls.order_customer1_order_item_data__for_update = {**cls.order_customer1_order_item_data, 'quantity': cls.order_customer1_order_item_data['quantity'] + 1}
        cls.order_customer2_order_item_data = model_to_dict(cls.order_customer2_order_item)
        cls.order_customer2_order_item_data__for_update = {**cls.order_customer2_order_item_data, 'quantity': cls.order_customer2_order_item_data['quantity'] + 1}

        # URLs for testing
        cls.update_order_url1 = reverse('order-update', args=[cls.order_customer1.pk])
        cls.update_order_url2 = reverse('order-update', args=[cls.order_customer2.pk])
        cls.create_order_url = reverse('order-create')
        cls.delete_order_url = reverse('order-delete', args=[cls.order_customer1.pk])
        cls.detail_order_url1 = reverse('order-detail', args=[cls.order_customer1.pk])
        cls.list_order_url = reverse('order-list')

        cls.create_order_item_url1 = reverse('orderitem-create', args=[cls.order_customer1.pk])
        cls.create_order_item_url2 = reverse('orderitem-create', args=[cls.order_customer2.pk])
        cls.update_order_item_url1 = reverse('orderitem-update', args=[cls.order_customer1_order_item.pk])
        # cls.update_order_item_url2 = reverse('orderitem-update', args=[cls.order_customer2_order_item.pk])
        cls.delete_order_item_url1 = reverse('orderitem-delete', args=[cls.order_customer1_order_item.pk])
        cls.detail_order_item_url1 = reverse('orderitem-detail', args=[cls.order_customer1_order_item.pk])



class OrderViewPermissionTest(BaseOrderTestData):
    """
    Test permissions for different user groups in the order views.

    Quick reference to HTTP response status codes used in tests:
    200 - OK
    302 - Redirect
    403 - Forbidden (doesn't have required permission)
    404 - Not found (has permission but resource is missing)
    """

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
             'data': self.order_customer1_data__for_update},
            {'user': self.shift_manager_user, 'expected_status': 302, 'method': 'post',
             'data': self.order_customer1_data__for_update},
            {'user': self.customer1_user, 'expected_status': 302, 'method': 'post',
             'data': self.order_customer1_data__for_update},
            {'user': self.customer2_user, 'expected_status': 403, 'method': 'post',
             'data': self.order_customer1_data__for_update},  # Cannot update another customer's order
            {'user': self.stock_personnel_user, 'expected_status': 403, 'method': 'post',
             'data': self.order_customer1_data__for_update},  # Stock personnel cannot update orders
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
             'data': self.order_customer1_data},
            {'user': self.shift_manager_user, 'expected_status': 302, 'method': 'post',
             'data': self.order_customer1_data},
            {'user': self.customer1_user, 'expected_status': 302, 'method': 'post',
             'data': self.order_customer1_data},
            {'user': self.stock_personnel_user, 'expected_status': 403, 'method': 'post',
             'data': self.order_customer1_data},
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


class OrderItemViewPermissionTest(BaseOrderTestData):
    """
    Test permissions for different user groups in the OrderItem views.

    Quick reference to HTTP response status codes used in tests:
    200 - OK
    302 - Redirect
    403 - Forbidden (doesn't have required permission)
    404 - Not found (has permission but resource is missing)
    """


    def test_orderitem_create_permissions(self):
        """ Test permissions for creating an order item. """
        test_cases = [
            {'user': self.customer1_user, 'expected_status': 200, 'method': 'get', 'data':None},
            {'user': self.customer2_user, 'expected_status': 403, 'method': 'get', 'data':None},
            {'user': self.shift_manager_user, 'expected_status': 200, 'method': 'get', 'data':None},
            {'user': self.staff_user, 'expected_status': 403, 'method': 'get', 'data':None},

            {'user': self.customer1_user, 'expected_status': 302, 'method': 'post', 'data': self.order_customer1_order_item_data},
            {'user': self.customer2_user, 'expected_status': 403, 'method': 'post', 'data': self.order_customer1_order_item_data},
            {'user': self.shift_manager_user, 'expected_status': 302, 'method': 'post', 'data': self.order_customer1_order_item_data},
            {'user': self.stock_personnel_user, 'expected_status': 403, 'method': 'post', 'data': self.order_customer1_order_item_data},
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
            {'user': self.customer1_user, 'expected_status': 302, 'method': 'post', 'data': self.order_customer1_order_item_data__for_update},
            {'user': self.customer2_user, 'expected_status': 403, 'method': 'post', 'data': self.order_customer1_order_item_data__for_update},
            {'user': self.shift_manager_user, 'expected_status': 302, 'method': 'post', 'data': self.order_customer1_order_item_data__for_update},
            {'user': self.staff_user, 'expected_status': 403, 'method': 'post', 'data': self.order_customer1_order_item_data__for_update},
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

