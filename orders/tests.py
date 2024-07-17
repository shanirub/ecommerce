from django.test import TestCase
from .models import Order, OrderItem
from users.models import User
from products.models import Category, Product
from ecommerce.utils import compare_model_instances


class OrderManagerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='shani',
            email='shani@example.com',
            password='abc12345')
        self.user2 = User.objects.create_user(
            username='nirit',
            email='nirit@example.com',
            password='aabb1234'
        )
        self.order = Order.objects.create_order(user=self.user)
        self.order2 = Order.objects.create_order(user=self.user)

    def test_create_order(self):
        self.assertEqual(Order.objects.count(), 2)
        self.assertEqual(self.order.user, self.user)

    def test_update_order(self):
        # mark order as paid
        updated_order = Order.objects.update_order(self.order.id, is_paid=True)
        self.assertIsNotNone(updated_order)
        self.assertTrue(updated_order.is_paid)

    def test_update_nonexistent_order(self):
        updated_order = Order.objects.update_order(5, is_paid=True)
        self.assertIsNone(updated_order)

    def test_get_order(self):
        order_id = self.order.id
        order = Order.objects.get_order(order_id)
        self.assertIsNotNone(order)

        result = compare_model_instances(order, self.order)
        self.assertEqual(len(result.keys()), 0)

    def test_get_order_by_user(self):
        orders = Order.objects.get_order_by_user(self.user)
        self.assertIsNotNone(orders)
        self.assertEqual(len(orders), 2)

        orders = Order.objects.get_order_by_user(self.user2)
        self.assertIsNotNone(orders)
        self.assertEqual(len(orders), 0)

    def test_get_nonexistent_order(self):
        order = Order.objects.get_order(5)
        self.assertIsNone(order)

    def test_delete_order(self):
        order_id = self.order.id
        result = Order.objects.delete_order(order_id)
        self.assertIsNotNone(result)
        self.assertEqual(result[0], 1)
        self.assertEqual(Order.objects.count(), 1)

    def test_delete_nonexistent_order(self):
        result = Order.objects.delete_order(5)
        self.assertIsNone(result)


class OrderItemManagerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='shani',
            email='shani@example.com',
            password='abc12345')
        self.user2 = User.objects.create_user(
            username='nirit',
            email='nirit@example.com',
            password='aabb1234'
        )
        self.order = Order.objects.create_order(user=self.user)
        self.category = Category.objects.create_category('Stuff', 'Stuff things')
        self.product = Product.objects.create_product('thingy', 'medium size thingy', 100, self.category, 4)

        # creating order_item with a Product object
        self.order_item = OrderItem.objects.create_order_item(self.order, self.product, 1)

    def test_create_order_item(self):
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(self.order.user, self.user)
        # check that product stock was updated after adding order item
        self.assertEqual(self.product.stock, 3)

    def test_update_order_item_enough_stock(self):
        """
        order_item.quantity == 1 -> order_item.quantity == 2
        product.stock == 3 -> product.stock == 2
        """
        order_item_id = self.order_item.id
        updated_order_item = OrderItem.objects.update_order_item(order_item_id, quantity=2)
        self.assertIsNotNone(updated_order_item)

        # Refresh from database
        self.order_item.refresh_from_db()
        self.product.refresh_from_db()

        self.assertEqual(self.order_item.quantity, 2)
        self.assertEqual(self.product.stock, 2)

    def test_update_order_item_not_enough_stock(self):
        order_item_id = self.order_item.id
        updated_order_item = OrderItem.objects.update_order_item(order_item_id, quantity=100)
        self.assertIsNone(updated_order_item)
        # stock and quantity should have stayed the same
        self.assertEqual(self.order_item.quantity, 1)
        self.assertEqual(self.product.stock, 3)

    def test_update_nonexistent_order_item(self):
        order_item_id = 5
        updated_order_item = OrderItem.objects.update_order_item(order_item_id, quantity=100)
        self.assertIsNone(updated_order_item)

    def test_get_order_item_by_id(self):
        order_item_id = self.order_item.id
        order_item = OrderItem.objects.get_order_item(order_item_id)
        self.assertIsNotNone(order_item)
        diff = compare_model_instances(order_item, self.order_item)
        self.assertEqual(len(diff), 0)

    def test_get_nonexistent_order_item(self):
        order_item_id = 5
        order_item = OrderItem.objects.get_order_item(order_item_id)
        self.assertIsNone(order_item)

    def test_delete_order_item(self):
        result = OrderItem.objects.delete_order_item(self.order_item.id)
        self.assertIsNotNone(result)
        self.assertEqual(result, (1, {'orders.OrderItem': 1}))

    def test_delete_nonexistent_order_item(self):
        order_item_id = 5
        result = OrderItem.objects.delete_order_item(order_item_id)
        self.assertIsNone(result)


class OrderIntegrationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='shani',
            email='shani@example.com',
            password='abc12345')
        # self.user2 = User.objects.create_user(
        #     username='nirit',
        #     email='nirit@example.com',
        #     password='aabb1234'
        # )
        self.order = Order.objects.create_order(user=self.user)
        self.category = Category.objects.create_category('Stuff', 'Stuff things')

        self.product = Product.objects.create_product('thingyM', 'medium size thingy', 100, self.category, 4)
        self.product2 = Product.objects.create_product('thingyL', 'large size thingy', 200, self.category, 8)
        self.product3 = Product.objects.create_product('thingyS', 'small size thingy', 50, self.category, 20)

        self.order_item = OrderItem.objects.create_order_item(self.order, self.product, 1)
        self.order_item2 = OrderItem.objects.create_order_item(self.order, self.product2, 1)
        self.order_item3 = OrderItem.objects.create_order_item(self.order, self.product3, 1)

    def test_add_multiple_items_to_order(self):
        self.assertIsNotNone(self.order_item)
        self.assertIsNotNone(self.order_item2)
        self.assertIsNotNone(self.order_item3)
        self.assertEqual(OrderItem.objects.count(), 3)

        order_items = OrderItem.objects.get_all_order_items_from_order(order=self.order)
        self.assertIsNotNone(order_items)
        self.assertEqual(len(order_items), 3)
        self.assertTrue(self.order_item in order_items
                        and self.order_item2 in order_items
                        and self.order_item3 in order_items)

    def test_delete_order_and_check_items_deleted(self):

        self.assertIsNotNone(self.order_item)
        self.assertIsNotNone(self.order_item2)
        self.assertIsNotNone(self.order_item3)
        self.assertEqual(OrderItem.objects.count(), 3)

        result = Order.objects.delete_order(self.order.id)
        self.assertIsNotNone(result)
        self.assertEqual(result, (1, {'orders.Order': 1}))

    def test_combine_two_order_items_of_the_same_product(self):
        # create new order_item with quantity 2
        # create new order_item (of the same product) with quantity 5
        # check order has only one order_item in list, with quantity 7
        # check product stock was deducted by 7
        pass


