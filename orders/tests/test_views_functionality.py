from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

import factory
from orders.models import Order, OrderItem
from orders.tests.factories import OrderItemFactory, OrderFactory
from products.tests.factories import CategoryFactory, ProductFactory, UserFactory
from django.contrib.auth.models import Group
from ecommerce.management.commands.assign_permissions import Command
from django.forms.models import model_to_dict



import logging

logger = logging.getLogger('django')

'''
functionality testing

testing CRUD operations using views

403 is used instead of 404, as to not reveal a resource is missing
'''

class OrderViewTest(TestCase):
    def setUp(self):
        # Set up permissions using assign_permissions script
        Command().handle()

        # create customer user
        customer_group = Group.objects.get(name='customers')
        self.customer_user = UserFactory(groups=[customer_group])

        # create valid order
        self.order = OrderFactory(user=self.customer_user)
        self.order_data = model_to_dict(self.order)

        self.assertEqual(Order.objects.count(), 1)

        # create invalid order data
        self.invalid_order_data = {**self.order_data, 'is_paid': 15}

        # URLs for testing
        self.update_url = reverse('order-update', args=[self.order.pk])
        self.create_url = reverse('order-create')
        self.delete_url = reverse('order-delete', args=[self.order.pk])
        self.detail_url = reverse('order-detail', args=[self.order.pk])
        # self.list_url = reverse('order-list') # TODO: do i need this?

    def test_create_order_successful(self):
        self.client.login(username=self.customer_user.username, password='password')
        response = self.client.get(self.create_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_order.html')

        response = self.client.post(self.create_url, data=self.order_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('order-list'))
        # order count increased by 1
        self.assertEqual(Order.objects.count(), 2)

    def test_create_order_invalid_data(self):
        self.client.login(username=self.customer_user.username, password='password')
        response = self.client.get(self.create_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_order.html')

        with self.assertRaises(ValidationError):
            response = self.client.post(self.create_url, data=self.invalid_order_data)

        # no new order was created - order count stays 1
        self.assertEqual(Order.objects.count(), 1)


    def test_read_order(self):
        self.client.login(username=self.customer_user.username, password='password')
        response = self.client.get(self.detail_url, args=[self.order.pk])
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'order_detail.html')

    def test_read_non_existent_order(self):
        NON_EXISTANT_ORDER_PK = 12345
        self.client.login(username=self.customer_user.username, password='password')
        # Replace pk in self.detail_url with NON_EXISTANT_ORDER_PK
        detail_url_non_existent = self.detail_url.replace(str(self.order.pk), str(NON_EXISTANT_ORDER_PK))

        response = self.client.get(detail_url_non_existent)
        self.assertEqual(response.status_code, 403)

    def test_update_order_successful(self):
        self.client.login(username=self.customer_user.username, password='password')
        response = self.client.get(self.update_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'update_order.html')

        response = self.client.post(self.update_url, args=[self.order.pk], data={'is_paid':not self.order.is_paid})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('order-list'))

    def test_update_order_invalid_data(self):
        self.client.login(username=self.customer_user.username, password='password')
        response = self.client.get(self.update_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'update_order.html')

        with self.assertRaises(ValidationError):
            response = self.client.post(self.update_url, data=self.invalid_order_data)

    def test_update_non_existent_order(self):
        NON_EXISTANT_ORDER_PK = 12345
        self.client.login(username=self.customer_user.username, password='password')

        # Replace pk in self.update_url with NON_EXISTANT_ORDER_PK
        update_url_non_existent = self.update_url.replace(str(self.order.pk), str(NON_EXISTANT_ORDER_PK))

        response = self.client.post(update_url_non_existent, data={'is_paid': not self.order.is_paid})
        self.assertEqual(response.status_code, 403)

    def test_delete_order_successful(self):
        self.client.login(username=self.customer_user.username, password='password')
        response = self.client.get(self.delete_url, args=[self.order.pk])
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'delete_order.html')

        response = self.client.post(self.delete_url, args=[self.order.pk])
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('order-list'))

        self.assertEqual(Order.objects.count(), 0)

    def test_delete_non_existent_order(self):
        NON_EXISTANT_ORDER_PK = 12345
        self.client.login(username=self.customer_user.username, password='password')

        # Replace the pk in self.delete_url with NON_EXISTANT_ORDER_PK
        delete_url_non_existent = self.delete_url.replace(str(self.order.pk), str(NON_EXISTANT_ORDER_PK))

        response = self.client.get(delete_url_non_existent)
        self.assertEqual(response.status_code, 403)

        response = self.client.post(delete_url_non_existent)
        self.assertEqual(response.status_code, 403)


class OrderItemViewTest(TestCase):
    def setUp(self):
        # Set up permissions using assign_permissions script
        Command().handle()

        # Create a customer user
        customer_group = Group.objects.get(name='customers')
        self.customer_user = UserFactory(groups=[customer_group])

        # Create a valid order and order item
        self.order = OrderFactory(user=self.customer_user)
        self.order_item = OrderItemFactory(order=self.order)
        self.order_item_data = model_to_dict(self.order_item)

        self.assertEqual(OrderItem.objects.count(), 1)

        # Create invalid order item data
        self.invalid_order_item_data = {**self.order_item_data, 'quantity': -5}

        # URLs for testing
        self.create_url = reverse('orderitem-create', args=[self.order.pk])
        self.update_url = reverse('orderitem-update', args=[self.order_item.pk])
        self.detail_url = reverse('orderitem-detail', args=[self.order_item.pk])
        self.delete_url = reverse('orderitem-delete', args=[self.order_item.pk])
        # self.list_url = reverse('orderitem-list')

    def test_create_order_item_successful(self):
        self.client.login(username=self.customer_user.username, password='password')
        response = self.client.get(self.create_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_order_item.html')

        response = self.client.post(self.create_url, data=self.order_item_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('order-list'))  # Adjust success_url if necessary
        self.assertEqual(OrderItem.objects.count(), 2)

    def test_create_order_item_invalid_data(self):
        self.client.login(username=self.customer_user.username, password='password')
        response = self.client.get(self.create_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_order_item.html')

        response = self.client.post(self.create_url, data=self.invalid_order_item_data)
        self.assertEqual(response.status_code, 200)  # Should stay on the same page due to validation errors
        self.assertEqual(OrderItem.objects.count(), 1)  # No new order item created

    def test_read_order_item(self):
        self.client.login(username=self.customer_user.username, password='password')
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'order_item_detail.html')

    def test_read_non_existent_order_item(self):
        NON_EXISTENT_ORDER_ITEM_PK = 12345
        self.client.login(username=self.customer_user.username, password='password')
        detail_url_non_existent = self.detail_url.replace(str(self.order_item.pk), str(NON_EXISTENT_ORDER_ITEM_PK))

        response = self.client.get(detail_url_non_existent)
        self.assertEqual(response.status_code, 403)

    def test_update_order_item_successful(self):
        self.client.login(username=self.customer_user.username, password='password')
        response = self.client.get(self.update_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'update_order_item.html')

        response = self.client.post(self.update_url, data={'quantity': self.order_item.quantity + 1, 'price': self.order_item.price})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('order-list'))

    def test_update_order_item_invalid_data(self):
        self.client.login(username=self.customer_user.username, password='password')
        response = self.client.get(self.update_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'update_order_item.html')

        response = self.client.post(self.update_url, data=self.invalid_order_item_data)
        self.assertEqual(response.status_code, 200)  # Stays on the page due to validation errors

    def test_update_non_existent_order_item(self):
        NON_EXISTENT_ORDER_ITEM_PK = 12345
        self.client.login(username=self.customer_user.username, password='password')
        update_url_non_existent = self.update_url.replace(str(self.order_item.pk), str(NON_EXISTENT_ORDER_ITEM_PK))

        response = self.client.post(update_url_non_existent, data={'quantity': 2, 'price': 100})
        self.assertEqual(response.status_code, 403)

    def test_delete_order_item_successful(self):
        self.client.login(username=self.customer_user.username, password='password')
        response = self.client.get(self.delete_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'delete_order_item.html')

        response = self.client.post(self.delete_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('order-list'))
        self.assertEqual(OrderItem.objects.count(), 0)

    def test_delete_non_existent_order_item(self):
        NON_EXISTENT_ORDER_ITEM_PK = 12345
        self.client.login(username=self.customer_user.username, password='password')
        delete_url_non_existent = self.delete_url.replace(str(self.order_item.pk), str(NON_EXISTENT_ORDER_ITEM_PK))

        response = self.client.get(delete_url_non_existent)
        self.assertEqual(response.status_code, 403)

        response = self.client.post(delete_url_non_existent)
        self.assertEqual(response.status_code, 403)
