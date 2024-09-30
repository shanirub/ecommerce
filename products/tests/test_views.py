from unicodedata import category

from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse

from ecommerce.management.commands.assign_permissions import Command
from products.models import Product, Category
from users.models import User
import factory
from products.tests.factories import UserFactory, GroupFactory, ProductFactory, CategoryFactory


class ProductViewTests(TestCase):
    """
    test views functionality

    permissions are tested in test_permission_views.py
    here user of shirt_manager group is being used: has all permissions
    """

    def get_product_data(self, **overrides):
        """
        create a dict of Product attributes using factory
        Product is not saved in db

        # TODO used for create/update views scenarios.
        # TODO check if needed, or factory boy features are enough

        :param overrides: dict of attributes and values to update
        :return: dict of Product attributes
        """
        product_data = factory.build(dict, FACTORY_CLASS=ProductFactory)
        product_data.update(overrides)
        return product_data

    def setUp(self):
        # Set up permissions using assign_permissions script
        Command().handle()

        # Create product and category
        self.category = CategoryFactory(name='cat', description='Sample category')
        self.product = ProductFactory(category=self.category)

        # user of shift managers group - has all permissions
        shift_manager_group = Group.objects.get(name='shift_manager')
        self.shift_manager_user = UserFactory(groups=[shift_manager_group])


    def test_update_product_view(self):
        self.client.login(username=self.shift_manager_user.username, password='password')
        response = self.client.get(reverse('update_product', kwargs={'pk': self.product.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'update_product.html')

    def test_create_product_view(self):
        self.client.login(username=self.shift_manager_user.username, password='password')
        response = self.client.get(reverse('create_product'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_product.html')

    def test_create_product_success(self):
        self.client.login(username=self.shift_manager_user.username, password='password')
        product_data = self.get_product_data(name='snowflake product', category=self.category.pk)
        response = self.client.post(reverse('create_product'), product_data)
        self.assertEqual(response.status_code, 302)  # Check if redirected
        self.assertRedirects(response, reverse('product_list'))
        self.assertTrue(Product.objects.filter(name='snowflake product').exists())  # Check if product was created

    def test_create_product_invalid_data(self):
        self.client.login(username=self.shift_manager_user.username, password='password')

        # create invalid dict for product creation
        product_data = ProductFactory.build().__dict__
        product_data.update({
            'name': '',  # Invalid: name is required
            'price': 'invalid_price',  # Invalid: price should be a number
        })
        del product_data['id']
        del product_data['category_id']  # Invalid: category is required

        response = self.client.post(reverse('create_product'), product_data)

        self.assertEqual(response.status_code, 200)  # Ensure no redirect
        self.assertIn('form', response.context)

        form = response.context['form']
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
        self.assertIn('price', form.errors)
        self.assertIn('category', form.errors)

        expected_errors = {
            'name': ['This field is required.'],
            'price': ['Enter a number.'],
            'category': ['This field is required.']
        }
        self.assertEqual(form.errors, expected_errors)

        # Ensure no product was created with invalid data
        self.assertFalse(Product.objects.filter(description=product_data['description']).exists())

    def test_update_product_invalid_data(self):
        self.client.login(username=self.shift_manager_user.username, password='password')
        product_data = self.get_product_data(description='', price='invalid_price')
        response = self.client.post(reverse('update_product', args=[self.product.pk]), product_data)

        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        form = response.context['form']
        self.assertFalse(form.is_valid())
        self.assertIn('price', form.errors)

    def test_update_non_existing_product(self):
        NON_EXISTING_PRODUCT_PK = 12345
        self.client.login(username=self.shift_manager_user.username, password='password')
        product_data = self.get_product_data()
        response = self.client.post(reverse('update_product', args=[NON_EXISTING_PRODUCT_PK]), product_data)
        self.assertIn(response.status_code, [404, 500])  # TODO: change after adding permissions


    def test_read_existing_product(self):
        self.client.login(username=self.shift_manager_user.username, password='password')
        response = self.client.get(reverse('product_detail', args=[self.product.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'product_detail.html')
        self.assertContains(response, self.product.name)
        self.assertContains(response, self.product.description)
        self.assertContains(response, f"${self.product.price}")

    def test_read_not_existing_product(self):
        NON_EXISTING_PRODUCT_PK = 12345
        self.client.login(username=self.shift_manager_user.username, password='password')
        response = self.client.get(reverse('product_detail', args=[NON_EXISTING_PRODUCT_PK]))
        self.assertIn(response.status_code, [404, 500])  # TODO: change after adding permissions


    def test_delete_existing_product(self):
        self.client.login(username=self.shift_manager_user.username, password='password')

        # GET request to load delete confirmation page
        response = self.client.get(reverse('delete_product', args=[self.product.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'delete_product.html')

        # POST request to simulate confirmation
        response = self.client.post(reverse('delete_product', args=[self.product.pk]))
        self.assertRedirects(response, reverse('product_list'))

        # check to see product was indeed deleted
        with self.assertRaises(Product.DoesNotExist):
            Product.objects.get(pk=self.product.pk)

    def test_delete_non_existing_product(self):
        NON_EXISTING_PRODUCT_PK = 12345
        self.client.login(username=self.shift_manager_user.username, password='password')
        response = self.client.get(reverse('delete_product', args=[NON_EXISTING_PRODUCT_PK]))
        self.assertEqual(response.status_code, 404)
        response = self.client.get(reverse('product_detail', args=[NON_EXISTING_PRODUCT_PK]))
        self.assertIn(response.status_code, [404, 500])  # TODO: change after adding permissions



class CategoryViewTests(TestCase):
    def setUp(self):
        # Set up permissions using assign_permissions script
        Command().handle()

        self.category = CategoryFactory(name='cat', description='Sample category')

        # user of shift managers group - has all permissions
        shift_manager_group = Group.objects.get(name='shift_manager')
        self.shift_manager_user = UserFactory(groups=[shift_manager_group])

    def test_create_category_view(self):
        self.client.login(username=self.shift_manager_user.username, password='password')
        response = self.client.get(reverse('create_category'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_category.html')

    def test_create_category_success(self):
        self.client.login(username=self.shift_manager_user.username, password='password')
        response = self.client.post(reverse('create_category'), {'name': 'new category', 'description': 'description'})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('category_list'))
        self.assertTrue(Category.objects.filter(name='new category').exists())

    def test_create_invalid_category(self):
        self.client.login(username=self.shift_manager_user.username, password='password')
        response = self.client.post(reverse('create_category'), {'name': '', 'description': 'description'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        form = response.context['form']
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)

        expected_errors = {'name': ['This field is required.']}
        self.assertEqual(form.errors, expected_errors)
        self.assertFalse(Category.objects.filter(description='description').exists())

    def test_update_non_existing_category(self):
        self.client.login(username=self.shift_manager_user.username, password='password')
        response = self.client.post(reverse('update_category', kwargs={'pk': '010101'}))
        self.assertIn(response.status_code, [404, 500])  # TODO: change after adding permissions


    def test_read_existing_category(self):
        self.client.login(username=self.shift_manager_user.username, password='password')
        response = self.client.get(reverse('category_detail', args=[self.category.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'category_detail.html')
        self.assertContains(response, self.category.name)

    def test_read_non_existing_category(self):
        NON_EXISTING_CATEGORY_PK = 12345
        self.client.login(username=self.shift_manager_user.username, password='password')
        response = self.client.get(reverse('category_detail', args=[NON_EXISTING_CATEGORY_PK]))
        self.assertIn(response.status_code, [404, 500])  # TODO: change after adding permissions


        with self.assertRaises(Category.DoesNotExist):
            Category.objects.get(pk=NON_EXISTING_CATEGORY_PK)

    def test_delete_existing_category(self):
        self.client.login(username=self.shift_manager_user.username, password='password')

        # GET request to load delete confirmation page
        response = self.client.get(reverse('delete_category', args=[self.category.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'delete_category.html')

        # POST request to simulate confirmation
        response = self.client.post(reverse('delete_category', args=[self.category.pk]))
        self.assertRedirects(response, reverse('category_list'))

        # check to see category was indeed deleted
        with self.assertRaises(Category.DoesNotExist):
            Category.objects.get(pk=self.category.pk)

    def test_delete_non_existing_category(self):
        NON_EXISTING_CATEGORY_PK = 12345
        self.client.login(username=self.shift_manager_user.username, password='password')
        response = self.client.post(reverse('delete_category', args=[NON_EXISTING_CATEGORY_PK]))
        self.assertIn(response.status_code, [404, 500])  # TODO: change after adding permissions

        with self.assertRaises(Category.DoesNotExist):
            Category.objects.get(pk=NON_EXISTING_CATEGORY_PK)
