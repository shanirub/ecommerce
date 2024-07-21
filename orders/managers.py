from typing import Union, Optional

from django.db import models, transaction
from products.managers import ProductManager
from django.core.exceptions import ValidationError
from products.models import Product


class OrderManager(models.Manager):
    def create_order(self, user, is_paid=False):
        return self.create(
            user=user, is_paid=is_paid)

    def update_order(self, order_id, **kwargs):
        try:
            order = self.get(id=order_id)
            for key, value in kwargs.items():
                setattr(order, key, value)
                order.save()
            return order
        except self.model.DoesNotExist:
            return None

    def delete_order(self, order_id):
        """
        delete an Order including all order_items in it
        :param order_id: id field of Order object
        :return:
        """
        try:
            order = self.get(id=order_id)
            with transaction.atomic():
                from orders.models import OrderItem
                order_items_to_delete = OrderItem.objects.get_all_order_items_from_order(order)
                if order_items_to_delete is None:
                    raise Exception(f"Failed getting a list of items to delete, when trying to delete order {order}")
                # if no order_items were found under order, order_items_to_delete should be an empty list
                for order_item in order_items_to_delete:
                    r = OrderItem.objects.delete_order_item(order_item.id)
                    if not r:
                        raise Exception(f"Deleting order_item {order_item} with id {order_item.id} failed."
                                        f"Deleting order {order} with id {order_id} failed.")
                result = order.delete()
                return result
        except self.model.DoesNotExist:
            return None
        except Exception as e:
            print(e)
            return None

    def get_order(self, order_id):
        try:
            order = self.get(id=order_id)
            return order
        except self.model.DoesNotExist:
            return None

    def get_order_by_user(self, user):
        try:
            orders = self.filter(user=user)
            return orders
        except self.model.DoesNotExist:
            return None


class OrderItemManager(models.Manager):
    def create_order_item(self, order: 'Order', product: Union[Product, str], quantity: int)\
            -> Optional['OrderItem']:
        """

        :param order: Order object
        :param product: Product object OR product's name (str)
        :param quantity: int
        :return: OrderItem object if was successful. None otherwise
        """
        try:
            if isinstance(product, str):
                product = Product.objects.get(name=product)

            updated_stock = product.stock - quantity
            price = product.price * quantity

            with transaction.atomic():
                '''
                Two transactions:
                 1. update product stock
                 2. create order_item
                 
                 transactions are atomic to ensure that order_item is created
                 only when product's stock was updated successfully
                '''
                # updating product stock
                updated_product = ProductManager.update_product(self, product, stock=updated_stock)
                if not updated_product:
                    raise ValidationError(f'Failed to create new order item with this attributes: '
                                          f'order= {order}, product= {product}, quantity= {quantity}')
                # creating order_item
                return self.create(order=order, product=product, quantity=quantity, price=price)
        except ValidationError as e:
            print(e)
            return None
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return None

    def update_order_item(self, order_item_id, **kwargs):
        try:
            with transaction.atomic():
                order_item = self.get(id=order_item_id)
                for key, value in kwargs.items():
                    if key == 'quantity':
                        old_quantity = order_item.quantity
                        new_quantity = value
                        change_in_stock = old_quantity - new_quantity
                        updated_product = ProductManager.update_product(
                            self, order_item.product, stock=order_item.product.stock + change_in_stock)
                        if not updated_product:
                            raise ValidationError(f"Failed to update order item with this attributes: "
                                                  f"order_item= {order_item}, key= {key}, value= {value}")
                        updated_product.save()
                        new_price = new_quantity * order_item.product.price
                        setattr(order_item, 'price', new_price)
                    setattr(order_item, key, value)

                order_item.save()
                return order_item
        except self.model.DoesNotExist:
            return None
        except ValidationError as e:
            print(e)
            return None
        except Exception as e:
            print(f"Unexpected error: {str(e)}")

    def delete_order_item(self, order_item_id):
        try:
            order_item = self.get(id=order_item_id)
            result = order_item.delete()
            return result
        except self.model.DoesNotExist:
            return None

    def get_order_item(self, order_item_id):
        try:
            order_item = self.get(id=order_item_id)
            return order_item
        except self.model.DoesNotExist:
            return None

    def get_all_order_items_from_order(self, order: 'Order'):
        """
        :return: returns a list of all order_item objects in order, None if something went wrong
        """
        try:
            order_items = self.filter(order=order)
            return order_items
        except self.model.DoesNotExist:
            return None
        except Exception as e:
            print(e)
            return None
