from django.test import TestCase
from django.urls import reverse
from products.models import Product, Category
from users.models import User
import factory
from products.tests.factories import UserFactory, GroupFactory, ProductFactory, CategoryFactory


class ProductViewTests(TestCase):

    def get_product_data(self, **overrides):
        product_data = factory.build(dict, FACTORY_CLASS=ProductFactory)
        product_data.update(overrides)
        return product_data

    def setUp(self):

        self.admin_user = UserFactory(username='admin', password='admin', is_superuser=True)
        self.category = CategoryFactory()
        self.product = ProductFactory(category=self.category)

    def test_update_product_view(self):
        self.client.login(username='admin', password='admin')
        response = self.client.get(reverse('update_product', kwargs={'pk': self.product.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'update_product.html')

    def test_create_product_view(self):
        self.client.login(username='admin', password='admin')
        response = self.client.get(reverse('create_product'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_product.html')

    def test_create_product_success(self):
        self.client.login(username='admin', password='admin')
        product_data = self.get_product_data(name='snowflake product', category=self.category.pk)
        response = self.client.post(reverse('create_product'), product_data)
        self.assertEqual(response.status_code, 302)  # Check if redirected
        self.assertRedirects(response, reverse('product_list'))
        self.assertTrue(Product.objects.filter(name='snowflake product').exists())  # Check if product was created

    def test_create_product_invalid_data(self):
        self.client.login(username='admin', password='admin')
        product_data = self.get_product_data(name='', price='invalid_price')
        response = self.client.post(reverse('create_product'), product_data)

        self.assertEqual(response.status_code, 200)  # Ensure no redirect
        self.assertIn('form', response.context)

        form = response.context['form']
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
        self.assertIn('price', form.errors)

        expected_errors = {
            'name': ['This field is required.'],
            'price': ['Enter a number.'],
        }
        self.assertEqual(form.errors, expected_errors)

        # Ensure no product was created with invalid data
        self.assertFalse(Product.objects.filter(description=product_data['description']).exists())

    def test_update_product_invalid_data(self):
        self.client.login(username='admin', password='admin')
        product_data = self.get_product_data(description='', price='invalid_price')
        response = self.client.post(reverse('update_product', args=[self.product.pk]), product_data)

        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        form = response.context['form']
        self.assertFalse(form.is_valid())
        self.assertIn('price', form.errors)

    def test_update_non_existing_product(self):
        NON_EXISTING_PRODUCT_PK = 12345
        self.client.login(username='admin', password='admin')
        product_data = self.get_product_data()
        response = self.client.post(reverse('update_product', args=[NON_EXISTING_PRODUCT_PK]), product_data)
        self.assertIn(response.status_code, [404, 500])  # TODO: change after adding permissions


    def test_read_existing_product(self):
        self.client.login(username='admin', password='admin')
        response = self.client.get(reverse('product_detail', args=[self.product.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'product_detail.html')
        self.assertContains(response, self.product.name)
        self.assertContains(response, self.product.description)
        self.assertContains(response, f"${self.product.price}")

    def test_read_not_existing_product(self):
        NON_EXISTING_PRODUCT_PK = 12345
        self.client.login(username='admin', password='admin')
        response = self.client.get(reverse('product_detail', args=[NON_EXISTING_PRODUCT_PK]))
        self.assertIn(response.status_code, [404, 500])  # TODO: change after adding permissions


    def test_delete_existing_product(self):
        self.client.login(username='admin', password='admin')

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
        self.client.login(username='admin', password='admin')
        response = self.client.get(reverse('delete_product', args=[NON_EXISTING_PRODUCT_PK]))
        self.assertEqual(response.status_code, 404)
        response = self.client.get(reverse('product_detail', args=[NON_EXISTING_PRODUCT_PK]))
        self.assertIn(response.status_code, [404, 500])  # TODO: change after adding permissions



class CategoryViewTests(TestCase):
    def setUp(self):
        self.admin_user = UserFactory(username='admin', password='admin', is_superuser=True)
        self.category = CategoryFactory()

    def test_create_category_view(self):
        self.client.login(username='admin', password='admin')
        response = self.client.get(reverse('create_category'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_category.html')

    def test_create_category_success(self):
        self.client.login(username='admin', password='admin')
        response = self.client.post(reverse('create_category'), {'name': 'new category', 'description': 'description'})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('category_list'))
        self.assertTrue(Category.objects.filter(name='new category').exists())

    def test_create_invalid_category(self):
        self.client.login(username='admin', password='admin')
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
        self.client.login(username='admin', password='admin')
        response = self.client.post(reverse('update_category', kwargs={'pk': '010101'}))
        self.assertIn(response.status_code, [404, 500])  # TODO: change after adding permissions


    def test_read_existing_category(self):
        self.client.login(username='admin', password='admin')
        response = self.client.get(reverse('category_detail', args=[self.category.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'category_detail.html')
        self.assertContains(response, self.category.name)

    def test_read_non_existing_category(self):
        NON_EXISTING_CATEGORY_PK = 12345
        self.client.login(username='admin', password='admin')
        response = self.client.get(reverse('category_detail', args=[NON_EXISTING_CATEGORY_PK]))
        self.assertIn(response.status_code, [404, 500])  # TODO: change after adding permissions


        with self.assertRaises(Category.DoesNotExist):
            Category.objects.get(pk=NON_EXISTING_CATEGORY_PK)

    def test_delete_existing_category(self):
        self.client.login(username='admin', password='admin')

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
        self.client.login(username='admin', password='admin')
        response = self.client.post(reverse('delete_category', args=[NON_EXISTING_CATEGORY_PK]))
        self.assertIn(response.status_code, [404, 500])  # TODO: change after adding permissions

        with self.assertRaises(Category.DoesNotExist):
            Category.objects.get(pk=NON_EXISTING_CATEGORY_PK)
