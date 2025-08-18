# from django.test import TestCase
# from users.models import CustomUser as User
# from django.core.exceptions import ValidationError
# from django.db import IntegrityError
# from django.db import models
# from unittest.mock import patch
#
# from tenants.models import Tenant, TenantAwareModel
#
#
# class TestCustomUser(TestCase):
#
#     def setUp(self):
#         self.tenant = Tenant.objects.create(
#             name="Test Tenant",
#             subdomain="testsubdoamin"
#         )
#
#     def test_create_user_with_valid_email(self):
#         user = User.objects.create_user(
#             email='test@example.com',
#             password='testpass123',
#             first_name='John',
#             last_name='Doe'
#         )
#
#         self.assertEqual(user.email, 'test@example.com')
#         self.assertEqual(user.first_name, 'John')
#         self.assertEqual(user.last_name, 'Doe')
#         self.assertTrue(user.check_password('testpass123'))
#         self.assertFalse(user.is_staff)
#         self.assertFalse(user.is_superuser)
#         self.assertTrue(user.is_active)
#
#     def test_create_superuser_with_valid_data(self):
#         superuser = User.objects.create_superuser(
#             email='admin@example.com',
#             password='adminpass123'
#         )
#
#         self.assertEqual(superuser.email, 'admin@example.com')
#         self.assertTrue(superuser.is_staff)
#         self.assertTrue(superuser.is_superuser)
#         self.assertTrue(superuser.is_active)
#         self.assertTrue(superuser.check_password('adminpass123'))
#
#     def test_add_user_with_tenant(self):
#         user = User.objects.create_user(
#             email='test@example.com',
#             password='testpass123',
#             first_name='John',
#             last_name='Doe'
#         )
#
#         self.assertEqual(user.tenant, self.tenant)
#
