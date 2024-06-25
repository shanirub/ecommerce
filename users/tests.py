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