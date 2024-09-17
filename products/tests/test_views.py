from django.test import TestCase
from django.urls import reverse
from users.models import User
from products.models import Product, Category


class ProductViewTests(TestCase):

    def get_product_data(self, product=None, **overrides):
        # TODO: move to separate utils file?
        data = {
            'name': product.name if product else 'Default Name',
            'description': product.description if product else 'Default Description',
            'price': product.price if product else 10.0,
            'stock': product.stock if product else 100,
            'category': product.category.id if product else self.category.id,
        }
        data.update(overrides)
        return data

    def setUp(self):
        self.admin_user = User.objects.create_superuser(username='admin', password='admin', email='admin@example.com')
        self.category = Category.objects.create_category(name='cat1', description='cat example')
        self.product = Product.objects.create(
            name='Test Product',
            description='Test Description',
            price=10.0,
            stock=100,
            category=self.category
        )

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
        product_data = self.get_product_data(self.product, name='snowflake product')
        response = self.client.post(reverse('create_product'), product_data)
        self.assertEqual(response.status_code, 302)  # Check if redirected
        self.assertRedirects(response, reverse('product_list'))
        self.assertTrue(Product.objects.filter(name=self.product.name).exists())  # Check if the product was created

    def test_create_product_invalid_data(self):
        self.client.login(username='admin', password='admin')
        product_data = self.get_product_data(self.product, name='', price='invalid_price', description='something else')
        response = self.client.post(reverse('create_product'), product_data)

        # If redirected, follow the redirect
        if response.status_code == 302:
            response = self.client.get(response.url)

        # Check if form is in the context
        self.assertIn('form', response.context)
        form = response.context['form']
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
        self.assertIn('price', form.errors)

        expected_errors = {
            'name': ['This field is required.'],
            'price': ['Enter a number.']
        }
        self.assertEqual(form.errors, expected_errors)

        # Ensure no product was created with invalid data
        self.assertFalse(Product.objects.filter(name='').exists())
        self.assertFalse(Product.objects.filter(description='something else').exists())

    def test_update_product_invalid_data(self):
        self.client.login(username='admin', password='admin')
        product_data = self.get_product_data(self.product, description='', price='invalid_price',
                                             category='New Category')
        response = self.client.post(reverse('update_product', args=[self.product.pk]), product_data)

        # TODO: should never redirect? should stay on page. redirect only on success
        # If redirected, follow the redirect
        if response.status_code == 302:
            response = self.client.get(response.url)

        self.assertEqual(response.status_code, 200)  # Check that it did not redirect

        # Check if form is in the context
        self.assertIn('form', response.context)
        form = response.context['form']

        self.assertTrue(form.errors)

        form = response.context['form']
        self.assertFalse(form.is_valid())
        self.assertIn('category', form.errors)
        self.assertIn('price', form.errors)

    def test_update_non_existing_product(self):
        NON_EXISTING_PRODUCT_PK = 12345
        self.client.login(username='admin', password='admin')
        product_data = self.get_product_data(self.product, description='', price='invalid_price',
                                             category='New Category')
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


        with self.assertRaises(Product.DoesNotExist):
            Product.objects.get(pk=NON_EXISTING_PRODUCT_PK)

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
        response = self.client.get(reverse('product_detail', args=[NON_EXISTING_PRODUCT_PK]))
        self.assertIn(response.status_code, [404, 500])  # TODO: change after adding permissions


        with self.assertRaises(Product.DoesNotExist):
            Product.objects.get(pk=NON_EXISTING_PRODUCT_PK)


class CategoryViewTests(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(username='admin', password='admin', email='admin@example.com')
        self.category = Category.objects.create_category(name='cat1', description='cat example')

    def test_create_category_view(self):
        self.client.login(username='admin', password='admin')
        response = self.client.get(reverse('create_category'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_category.html')

    def test_create_category_success(self):
        self.client.login(username='admin', password='admin')
        response = self.client.post(reverse('create_category'), {'name': 'new category', 'description': 'description'})

        self.assertEqual(response.status_code, 302)  # Check if redirected
        self.assertRedirects(response, reverse('category_list'))
        self.assertTrue(Category.objects.filter(name='new category').exists())  # Check if the product was created

    def test_update_category_view(self):
        self.client.login(username='admin', password='admin')
        response = self.client.get(reverse('update_category', kwargs={'pk': self.category.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'update_category.html')

    def test_create_invalid_category(self):
        self.client.login(username='admin', password='admin')
        response = self.client.post(reverse('create_category'), {'name': '', 'description': 'description'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_category.html')

        # Check if form is in the context
        self.assertIn('form', response.context)
        form = response.context['form']
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)

        expected_errors = {
            'name': ['This field is required.'],
        }
        self.assertEqual(form.errors, expected_errors)

        # Ensure no product was created with invalid data
        self.assertFalse(Category.objects.filter(name='').exists())
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
