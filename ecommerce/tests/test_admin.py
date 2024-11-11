from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class AdminSiteTests(TestCase):
    def setUp(self):
        """ create a superuser and a normal user"""
        self.admin_user = get_user_model().objects.create_superuser(
            username='root',
            email='admin@example.com',
            password='testpass123'
        )
        self.client.force_login(self.admin_user)
        self.user = get_user_model().objects.create_user(
            username='some_user',
            email='user@example.com',
            password='testpass123',
        )

    def test_users_listed(self):
        """ check users listed on user page"""
        url = reverse('admin:users_user_changelist')
        res = self.client.get(url)
        self.assertContains(res, self.user.username)
        self.assertContains(res, self.user.email)

    def test_user_change_page(self):
        """ check user edit page """
        url = reverse('admin:users_user_change', args=[self.user.id])
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)

