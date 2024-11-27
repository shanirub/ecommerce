from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse

from ecommerce.management.commands.assign_permissions import Command
from orders.models import Order
from orders.tests.factories import OrderFactory, OrderItemFactory
import logging

from products.tests.factories import UserFactory, CategoryFactory, ProductFactory

logger = logging.getLogger('django')

'''
integration testing

testing complete flows
'''

class TestViewIntegration(TestCase):
    # TODO: add consts for quantity stock price ...
    # TODO: add testing for with_total_prices()

    @classmethod
    def setUpTestData(cls):
        # stuff that remain for all tests in class

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
        cls.customer2_user = UserFactory(groups=[customer_group])
        cls.stock_personnel_user = UserFactory(groups=[stock_group])

        # categories
        cls.category1 = CategoryFactory()
        cls.category2 = CategoryFactory()

        # products
        cls.products = []

        temp = ProductFactory(category=cls.category1)
        cls.products.append(temp)
        print(f"added product {temp} with price {temp.price}")

        temp = ProductFactory(category=cls.category2)
        cls.products.append(temp)
        print(f"added product {temp} with price {temp.price}")



    # def setUp(self):
    #     # stuff that loads before each test and then rolled back
    #     pass

    def test_create_order_and_verify_total(self):
        # log in as customer1
        self.client.force_login(self.customer1_user)

        # Create an order
        order = OrderFactory(user=self.customer1_user)
        response = self.client.get(reverse('order-detail', kwargs={'pk': order.pk}))
        self.assertEqual(response.status_code, 200)

        print(f"product list: {self.products}")

        # Add an item to the order
        # TODO: doesn't work, should create order_item and product in another way
        order_item = OrderItemFactory(order=order, product=self.products[0], quantity=2)
        order.refresh_from_db()

        # assert updated stock in product
        self.assertEqual(self.products[0].stock, 10)

        # Assert the order total is updated
        total_price = Order.objects.get_total_price(order.id)
        self.assertEqual(total_price, self.products[0].price * 2)

        # Verify the order detail page shows the correct total
        response = self.client.get(reverse('order-detail', kwargs={'pk': order.pk}))
        self.assertContains(response, total_price)

    def test_update_order_item(self):
        current_quantity = 1
        new_quantity = 3

        self.client.force_login(self.customer1_user)
        order = OrderFactory(user=self.customer1_user)
        order_item = OrderItemFactory(order=order, product=self.products[1], quantity=current_quantity)

        logger.debug(f"Sending post request to update existing order item quantity 1 -> 3 ...")
        # Update the order item's quantity

        response = self.client.post(
            reverse('orderitem-update', args=[order_item.pk]),  # Pass the pk in the URL
            {'quantity': new_quantity,}  # Pass the update data as form data
        )

        self.assertEqual(response.status_code, 302)

        # Assert the order total updates
        order.refresh_from_db()
        total_price = Order.objects.get_total_price(order.id)
        # TODO: quantity change for order item is not saved
        # TODO: rewrite nicely
        # TODO: debug in update_order_item()
        self.assertEqual(total_price, self.products[1].price * 3)
        self.assertEqual(order_item.price, self.products[1].price * 3)

    def test_delete_order_item_updates_order_total(self):
        self.client.force_login(self.customer1_user)
        order = OrderFactory(user=self.customer1_user)
        order_item = OrderItemFactory(order=order, product=self.products[0], quantity=2)

        # Delete the order item
        response = self.client.post(reverse('orderitem-delete', kwargs={'pk': order_item.pk}))
        self.assertEqual(response.status_code, 302)

        # Assert the order total is updated to 0
        order.refresh_from_db()
        total_price = Order.objects.get_total_price(order.id)
        self.assertEqual(total_price, 0.00)
    #
    # def test_add_invalid_item_to_order(self):
    #     user = UserFactory()
    #     self.client.force_login(user)
    #
    #     product = ProductFactory(price=10.00)
    #     order = OrderFactory(user=user)
    #
    #     # Try to add an invalid quantity
    #     response = self.client.post(reverse('order_item_create'), {
    #         'order': order.pk,
    #         'product': product.pk,
    #         'quantity': -1
    #     })
    #     self.assertEqual(response.status_code, 400)  # Or appropriate error code
    #
    #     # Assert the order total remains unchanged
    #     order.refresh_from_db()
    #     self.assertEqual(order.total_price, 0.00)

    '''
    0, generate ten products of two categories
        a. create new customer
    1. customer creates new order
    2. customer adds products as order items
        a. view list
    3. customer updates order items
        a. view list
    4. customer deletes order items
        s. view list
    5. mock a payment? is_paid=True
    '''

    '''
    0, generate ten products of two categories
        a. create customer1
    1. customer1 creates new order
    2. customer1 adds products as order items
        a. view list
    3. create customer2
    4. customer2 tries to
        a. delete order
        b. delete order item
        c. update order item
        d. view order list
        e. view items in order
        f. delete order
    '''

    '''
    the same as before but with shift manager, stock personnel, staff
    '''



