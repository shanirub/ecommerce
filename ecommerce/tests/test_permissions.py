from django.contrib.auth.models import Group, Permission
from django.test import TestCase
from ecommerce.management.commands.assign_permissions import Command


class PermissionTests(TestCase):

    def setUp(self):
        # Run the assign_permissions command to set up permissions
        command = Command()
        command.handle()

        # Fetch all groups
        self.customers_group = Group.objects.get(name="customers")
        self.staff_group = Group.objects.get(name="staff")
        self.stock_personnel_group = Group.objects.get(name="stock_personnel")
        self.shift_manager_group = Group.objects.get(name="shift_manager")

        # Fetch relevant permissions
        self.product_permissions = Permission.objects.filter(content_type__model='product')
        self.order_permissions = Permission.objects.filter(content_type__model='order')
        self.orderitem_permissions = Permission.objects.filter(content_type__model='orderitem')
        self.user_permissions = Permission.objects.filter(content_type__model='user')
        self.category_permissions = Permission.objects.filter(content_type__model='category')

    def test_customers_group_permissions(self):
        # Test that customers can read products and create/update/delete orders and order items
        customer_perms = self.customers_group.permissions.all()

        # Product read permission
        self.assertIn(self.product_permissions.get(codename='view_product'), customer_perms)
        # Customers cannot create, update, or delete products
        self.assertNotIn(self.product_permissions.get(codename='add_product'), customer_perms)
        self.assertNotIn(self.product_permissions.get(codename='change_product'), customer_perms)
        self.assertNotIn(self.product_permissions.get(codename='delete_product'), customer_perms)

        # Order permissions
        self.assertIn(self.order_permissions.get(codename='add_order'), customer_perms)
        self.assertIn(self.order_permissions.get(codename='change_order'), customer_perms)
        self.assertIn(self.order_permissions.get(codename='delete_order'), customer_perms)

        # OrderItem permissions
        self.assertIn(self.orderitem_permissions.get(codename='add_orderitem'), customer_perms)
        self.assertIn(self.orderitem_permissions.get(codename='change_orderitem'), customer_perms)
        self.assertIn(self.orderitem_permissions.get(codename='delete_orderitem'), customer_perms)

    def test_staff_group_permissions(self):
        # Test that staff can create, update, and delete users and manage products and categories
        staff_perms = self.staff_group.permissions.all()

        # Product permissions
        self.assertIn(self.product_permissions.get(codename='add_product'), staff_perms)
        self.assertIn(self.product_permissions.get(codename='change_product'), staff_perms)
        self.assertIn(self.product_permissions.get(codename='delete_product'), staff_perms)

        # Category permissions
        self.assertIn(self.category_permissions.get(codename='add_category'), staff_perms)
        self.assertIn(self.category_permissions.get(codename='change_category'), staff_perms)
        self.assertIn(self.category_permissions.get(codename='delete_category'), staff_perms)

        # User management permissions
        self.assertIn(self.user_permissions.get(codename='add_user'), staff_perms)
        self.assertIn(self.user_permissions.get(codename='change_user'), staff_perms)
        self.assertIn(self.user_permissions.get(codename='delete_user'), staff_perms)

        # Staff cannot create or update orders or order items
        self.assertNotIn(self.order_permissions.get(codename='add_order'), staff_perms)
        self.assertNotIn(self.order_permissions.get(codename='change_order'), staff_perms)
        self.assertNotIn(self.order_permissions.get(codename='delete_order'), staff_perms)

    def test_stock_personnel_group_permissions(self):
        # Stock personnel can only update product price and quantity
        stock_perms = self.stock_personnel_group.permissions.all()

        # They should have permission to update products
        self.assertIn(self.product_permissions.get(codename='change_product'), stock_perms)

        # But should not create or delete products
        self.assertNotIn(self.product_permissions.get(codename='add_product'), stock_perms)
        self.assertNotIn(self.product_permissions.get(codename='delete_product'), stock_perms)

        # Stock personnel cannot modify orders, order items, or users
        self.assertNotIn(self.order_permissions.get(codename='add_order'), stock_perms)
        self.assertNotIn(self.orderitem_permissions.get(codename='add_orderitem'), stock_perms)
        self.assertNotIn(self.user_permissions.get(codename='add_user'), stock_perms)

    def test_shift_manager_group_permissions(self):
        # Shift managers should have permissions from both customers and staff
        shift_manager_perms = self.shift_manager_group.permissions.all()

        # Ensure shift managers have customer permissions for orders and order items
        self.assertIn(self.order_permissions.get(codename='add_order'), shift_manager_perms)
        self.assertIn(self.orderitem_permissions.get(codename='add_orderitem'), shift_manager_perms)

        # Ensure shift managers have staff permissions for products and categories
        self.assertIn(self.product_permissions.get(codename='add_product'), shift_manager_perms)
        self.assertIn(self.category_permissions.get(codename='add_category'), shift_manager_perms)

        # Ensure shift managers can manage users (staff privilege)
        self.assertIn(self.user_permissions.get(codename='add_user'), shift_manager_perms)
