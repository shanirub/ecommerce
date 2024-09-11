from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
User = get_user_model()


class UserFlowTestCase(TestCase):
    def setUp(self):
        # Set up a test user
        self.user = User.objects.create_user(username='testuser', password='testpassword')

    def test_full_logout_flow(self):
        # Step 1: Log in the user
        self.client.login(username='testuser', password='testpassword')

        # Step 2: Access a protected page (profile)
        profile_url = reverse('profile')
        response = self.client.get(profile_url)
        self.assertEqual(response.status_code, 200)  # Profile page should load correctly
        self.assertContains(response, 'Welcome, testuser!')  # Ensure the user is on the profile page

        # Step 3: Log out via POST request
        logout_url = reverse('logout')
        response = self.client.post(logout_url)

        # Step 4: After logout, ensure the logged_out.html page is shown
        self.assertEqual(response.status_code, 200)  # User should see logged_out.html first
        self.assertContains(response, 'You have been logged out.')  # Verify logged_out.html content

        # Step 5: Simulate trying to access the profile page again (should redirect to login)
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 302)  # Check if the user is redirected to the login page
        # Allow for the 'next' parameter in the redirect URL
        expected_url = reverse('login') + '?next=' + reverse('profile')
        self.assertRedirects(response, expected_url)

        # Step 6: Verify the user is logged out
        self.assertFalse(response.wsgi_request.user.is_authenticated)  # Ensure the user is logged out

    def test_logout_failed_not_logged_in(self):
        """
        using django's default LogoutView behavior
        """
        logout_url = reverse('logout')
        response = self.client.post(logout_url)
        # Check if the response is successful (200 OK)
        self.assertEqual(response.status_code, 200)
        # Check that the user is not authenticated
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        self.assertContains(response, 'You have been logged out.')


class UserRegistrationTestCase(TestCase):
    def setUp(self):
        self.signup_url = reverse('signup')
        self.signup_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'testpassword',
            'password2': 'testpassword',
        }
        self.signup_data_invalid_email = {**self.signup_data, 'email': 'aaa'}
        self.signup_data_password_mismatch = {**self.signup_data, 'password1': 'aaa'}

        self.other_user_signup_data = {**self.signup_data, 'username': 'nirit'}
        self.other_user_data = {
            'username': 'nirit',
            'email': 'test@example.com',
            'password': 'testpassword',
        }
        self.other_user = User.objects.create_user(**self.other_user_data)

    def test_user_registration(self):
        # registration
        response = self.client.post(self.signup_url, self.signup_data)
        # successful registration -> redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))
        # user was created, but not logged in
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        # check to see if user was created
        self.assertTrue(User.objects.filter(username=self.signup_data['username']).exists())

    def test_user_registration_failed_password_match(self):
        response = self.client.post(self.signup_url, self.signup_data_password_mismatch)
        # no redirection to login
        self.assertEqual(response.status_code, 200)
        # Check for form errors
        form = response.context['form']
        self.assertTrue(form.errors)
        self.assertIn('password2', form.errors)
        # user was not created in db
        self.assertFalse(User.objects.filter(username=self.signup_data['username']).exists())

    def test_user_registration_failed_invalid_email(self):
        response = self.client.post(self.signup_url, self.signup_data_invalid_email)
        # no redirection to login
        self.assertEqual(response.status_code, 200)
        # Check for form errors
        form = response.context['form']
        self.assertTrue(form.errors)
        self.assertIn('email', form.errors)

        # user was not created in db
        self.assertFalse(User.objects.filter(username=self.signup_data['username']).exists())

    def test_user_registration_failed_already_exists(self):
        response = self.client.post(self.signup_url, self.other_user_signup_data)
        self.assertEqual(response.status_code, 200)
        # Check for form errors
        form = response.context['form']
        self.assertTrue(form.errors)
        self.assertIn('username', form.errors)  # Error should be related to the username already existing


class UserLoginTestCase(TestCase):
    def setUp(self):
        self.signup_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpassword',
        }
        self.user = User.objects.create_user(**self.signup_data)

        self.login_url = reverse('login')
        self.login_data = {
            'username': 'testuser',
            'password': 'testpassword',
        }
        self.login_data_bad_password = {
            'username': 'testuser',
            'password': 'testpassword222',
        }
        self.login_data_bad_username = {
            'username': 'testuserddd',
            'password': 'testpassword',
        }

    def test_user_login_success(self):
        response = self.client.post(self.login_url, self.login_data)
        # successful login -> redirect to profile
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('profile'))
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_user_failed_login_bad_password(self):
        response = self.client.post(self.login_url, self.login_data_bad_password)
        self.assertEqual(response.status_code, 200)
        # Check for form errors
        form = response.context['form']
        self.assertTrue(form.errors)
        self.assertIn('__all__', form.errors)  # Login form errors are usually stored under `__all__`

    def test_user_failed_login_bad_username(self):
        response = self.client.post(self.login_url, self.login_data_bad_username)
        self.assertEqual(response.status_code, 200)
        # Check for form errors
        form = response.context['form']
        self.assertTrue(form.errors)
        self.assertIn('__all__', form.errors)  # Login form errors are usually stored under `__all__`


