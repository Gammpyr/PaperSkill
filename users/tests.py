from django.test import TestCase

# users/tests.py
from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class UserModelTest(TestCase):
    """Тесты для модели пользователя"""

    def test_create_user(self):
        """Тест создания пользователя"""
        user = User.objects.create_user(
            phone_number='+79876543210',
            password='testpassword123',
            username='testuser',
            email='test@example.com'
        )

        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.phone_number, '+79876543210')
        self.assertTrue(user.check_password('testpassword123'))
        self.assertFalse(user.is_staff)
        self.assertTrue(user.is_active)

    def test_create_superuser(self):
        """Тест создания суперпользователя"""
        admin = User.objects.create_superuser(
            phone_number='+79999999999',
            password='admin123',
            username='admin'
        )

        self.assertEqual(admin.username, 'admin')
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)

    def test_user_string_representation(self):
        """Тест строкового представления пользователя"""
        user = User.objects.create_user(
            phone_number='+79876543210',
            password='testpassword123',
            username='testuser'
        )

        self.assertEqual(str(user), '+79876543210')