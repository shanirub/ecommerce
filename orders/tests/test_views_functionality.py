from django.test import TestCase
from django.urls import reverse

import factory

from products.models import Product, Category
from orders.models import Order, OrderItem
from factories import OrderItemFactory, OrderFactory
from products.tests.factories import CategoryFactory, ProductFactory, UserFactory
from django.contrib.auth.models import Group


import logging

logger = logging.getLogger('django')

'''
functionality testing

testing CRUD operations using views
'''

class OrderViewTest(TestCase):
    def setUp(self):
        # create customer user
        customer_group = Group.objects.get(name='customers')
        self.customer_user = UserFactory(groups=[customer_group])

        pass

    def test_create_order_successful(self):
        self.client.login(username=self.customer_user.username, password='password')
        response = self.client.get(reverse('order-create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_order.html')

        data = factory.build(dict, FACTORY_CLASS=OrderFactory)
        response = self.client.post(reverse('order-create'), data=data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('order_list'))
        self.assertTrue(Order.objects.filter(user=self.customer_user.username).exists())

    def test_create_order_invalid_data(self):
        pass

    def test_read_order(self):
        pass

    def test_non_existent_order(self):
        pass

    def test_update_order_successful(self):
        pass

    def test_update_order_invalid_data(self):
        pass

    def test_update_non_existent_order(self):
        pass

    def test_delete_order_successful(self):
        pass

    def test_delete_non_existent_order(self):
        pass


class OrderItemViewTest(TestCase):
    def setUp(self):
        # create customer user
        pass

    def test_create_order_item_successful(self):
        pass

    def test_create_order_item_invalid_data(self):
        pass

    def test_read_order_item(self):
        pass

    def test_non_existent_order_item(self):
        pass

    def test_update_order_item_successful(self):
        pass

    def test_update_order_item_invalid_data(self):
        pass

    def test_update_non_existent_order_item(self):
        pass

    def test_delete_order_item_successful(self):
        pass

    def test_delete_non_existent_order_item(self):
        pass