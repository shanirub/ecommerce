from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from products.models import Product, Category
from orders.models import Order, OrderItem
from users.models import User

import logging

logger = logging.getLogger('django')


class Command(BaseCommand):
    help = 'Assigns permissions to groups based on predefined roles'

    def add_arguments(self, parser):
        pass  # If needed for command arguments

    def handle(self, *args, **kwargs):
        logger.info("Starting with permissions assignment...")
        # Define groups
        customers_group, created = Group.objects.get_or_create(name='customers')
        staff_group, created = Group.objects.get_or_create(name='staff')
        stock_personnel_group, created = Group.objects.get_or_create(name='stock_personnel')
        shift_manager_group, created = Group.objects.get_or_create(name='shift_manager')

        # Get content types for models
        product_content_type = ContentType.objects.get_for_model(Product)
        category_content_type = ContentType.objects.get_for_model(Category)
        order_content_type = ContentType.objects.get_for_model(Order)
        order_item_content_type = ContentType.objects.get_for_model(OrderItem)
        user_content_type = ContentType.objects.get_for_model(User)

        # Get permissions
        product_permissions = Permission.objects.filter(content_type=product_content_type)
        category_permissions = Permission.objects.filter(content_type=category_content_type)
        order_permissions = Permission.objects.filter(content_type=order_content_type)
        order_item_permissions = Permission.objects.filter(content_type=order_item_content_type)
        user_permissions = Permission.objects.filter(content_type=user_content_type)

        # Assign permissions based on the table
        # Customers Group
        customers_group.permissions.set([
            product_permissions.get(codename='view_product'),
            category_permissions.get(codename='view_category'),
            order_permissions.get(codename='add_order'),
            order_permissions.get(codename='view_order'),
            order_permissions.get(codename='change_order'),
            order_permissions.get(codename='delete_order'),
            order_item_permissions.get(codename='add_orderitem'),
            order_item_permissions.get(codename='view_orderitem'),
            order_item_permissions.get(codename='change_orderitem'),
            order_item_permissions.get(codename='delete_orderitem'),
        ])
        logger.debug("Done with customers_group permissions")

        # Staff Group
        staff_group.permissions.set([
            product_permissions.get(codename='add_product'),
            product_permissions.get(codename='view_product'),
            product_permissions.get(codename='change_product'),  # Limiting this to specific fields requires view logic
            product_permissions.get(codename='delete_product'),
            category_permissions.get(codename='add_category'),
            category_permissions.get(codename='view_category'),
            category_permissions.get(codename='change_category'),
            category_permissions.get(codename='delete_category'),
            order_permissions.get(codename='view_order'),  # Staff can only view orders, not modify them
            order_item_permissions.get(codename='view_orderitem'),  # Staff can only view order items
            user_permissions.get(codename='add_user'),
            user_permissions.get(codename='view_user'),
            user_permissions.get(codename='change_user'),
            user_permissions.get(codename='delete_user'),
        ])
        logger.debug("Done with staff_group permissions")

        # Stock Personnel Group
        stock_personnel_group.permissions.set([
            product_permissions.get(codename='view_product'),
            product_permissions.get(codename='change_product'),  # Limiting this to price/quantity requires view logic
            category_permissions.get(codename='view_category'),
        ])
        logger.debug("Done with stock_personnel_group permissions")

        # Shift Manager Group (Combination of Customers and Staff permissions)
        shift_manager_group.permissions.set([
            # Customers permissions
            product_permissions.get(codename='view_product'),
            category_permissions.get(codename='view_category'),
            order_permissions.get(codename='add_order'),
            order_permissions.get(codename='view_order'),
            order_permissions.get(codename='change_order'),
            order_permissions.get(codename='delete_order'),
            order_item_permissions.get(codename='add_orderitem'),
            order_item_permissions.get(codename='view_orderitem'),
            order_item_permissions.get(codename='change_orderitem'),
            order_item_permissions.get(codename='delete_orderitem'),

            # Staff permissions
            product_permissions.get(codename='add_product'),
            product_permissions.get(codename='change_product'),  # Again, field-specific logic may apply
            product_permissions.get(codename='delete_product'),
            category_permissions.get(codename='add_category'),
            category_permissions.get(codename='change_category'),
            category_permissions.get(codename='delete_category'),
            user_permissions.get(codename='add_user'),
            user_permissions.get(codename='view_user'),
            user_permissions.get(codename='change_user'),
            user_permissions.get(codename='delete_user'),
        ])
        logger.debug("Done with shift_manager_group permissions")

        # Feedback to console
        logger.info('Permissions successfully assigned to groups!')
