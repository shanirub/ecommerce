from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
User = get_user_model()


class UserRegistrationTestCase(TestCase):
    def test_user_registration(self):
        url = reverse('signup')  # Assuming 'register' is the URL name for the registration view
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'testpassword',
            'password2': 'testpassword',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)  # Check for successful redirect
        self.assertTrue(User.objects.filter(username='testuser').exists())  # Check if user is added to the database
        self.assertFalse(User.objects.filter(username='no_such_user').exists()) # (no false positive)

    def test_user_login(self):
        user = User.objects.create_user(username='testuser', password='testpassword')
        url = reverse('login')
        data = {
            'username': 'testuser',
            'password': 'testpassword',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    # def test_protected_view(self):
    #     user = User.objects.create_user(username='testuser', password='testpassword')
    #     self.client.login(username='testuser', password='testpassword')
    #     response = self.client.get(reverse('some_protected_view'))
    #     self.assertEqual(response.status_code, 200)
