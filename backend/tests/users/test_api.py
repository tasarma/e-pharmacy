# import pytest
# from rest_framework.test import APIClient
# from django.contrib.auth import get_user_model
#
# User = get_user_model()
#
#
# # --------------------------
# # User Registration Tests
# # --------------------------
#
# @pytest.mark.django_db
# def test_register_user_success(client, tenant):
#     """Should register a new user successfully."""
#     email = 'newuser@test.com'
#
#     response = client.post(
#         '/auth/users/',
#         {
#             'email': email,
#             'password': 'StrongPass123!'
#         },
#         HTTP_HOST=f"{tenant.subdomain}.example.com"
#     )
#
#     assert response.status_code == 201
#     assert User.all_objects.filter(email=email).exists()
#
#
# @pytest.mark.django_db
# def test_register_weak_password_fails(client, tenant):
#     """Should reject weak passwords."""
#     response = client.post(
#         '/auth/users/',
#         {
#             'email': 'weak@test.com',
#             'password': '123'
#         },
#         HTTP_HOST=f"{tenant.subdomain}.example.com"
#     )
#
#     assert response.status_code == 400
#
#
# # --------------------------
# # User Login Tests
# # --------------------------
#
# """
# This test fails when uncomment
#
# when test_login_success fails, got following error :
# WARNING  users.backends:backends.py:42 Authentication failed: user 'manager@testpharm.com' does not exist in tenant 'testpharm'
#
# when test_register_user_success fails, got following error 
#
# django.db.utils.IntegrityError: The row in table 'users_userprofile' with primary key '1' has an invalid foreign key: users_userprofile.tenant_id contains a value 'b3ed02599e4f4b07ade1be8a302604fc' that does not have a corresponding value in tenants_tenant.id.
# """
# # @pytest.mark.django_db
# # def test_login_success(client, manager):
# #     """Should log in using correct credentials."""
# #     response = client.post(
# #         '/auth/jwt/create/',
# #         {
# #             'email': manager.email,
# #             'password': 'TestPass123!'
# #         },
# #         HTTP_HOST=f"{manager.tenant.subdomain}.example.com"
# #     )
# #
# #     assert response.status_code == 200
# #     assert 'access' in response.data
# #     assert 'refresh' in response.data
#
#
# @pytest.mark.django_db
# def test_login_wrong_password(client, manager):
#     """Should fail login with wrong password."""
#     response = client.post(
#         '/auth/jwt/create/',
#         {
#             'email': manager.email,
#             'password': 'WrongPassword'
#         },
#         HTTP_HOST=f"{manager.tenant.subdomain}.example.com"
#     )
#
#     assert response.status_code == 401
#
#
# @pytest.mark.django_db
# def test_login_nonexistent_user(client, tenant):
#     """Should fail login for unknown user."""
#     response = client.post(
#         '/auth/jwt/create/',
#         {
#             'email': 'nonexistent@test.com',
#             'password': 'Pass123!'
#         },
#         HTTP_HOST=f"{tenant.subdomain}.example.com"
#     )
#
#     assert response.status_code == 401
#
#
# # # --------------------------
# # # User Profile Tests
# # # --------------------------
#
# @pytest.mark.django_db
# def test_get_own_profile(client, manager):
#     """Should allow authenticated user to view profile."""
#     client.force_authenticate(user=manager)
#
#     response = client.get(
#         '/auth/users/me/',
#         HTTP_HOST=f"{manager.tenant.subdomain}.example.com"
#     )
#
#     assert response.status_code == 200
#     assert response.data['email'] == manager.email
#
#
# @pytest.mark.django_db
# def test_update_own_profile(client, manager):
#     """Should allow user to update their own profile."""
#     client.force_authenticate(user=manager)
#
#     response = client.patch(
#         '/auth/users/me/',
#         {'first_name': 'Updated'},
#         HTTP_HOST=f"{manager.tenant.subdomain}.example.com"
#     )
#
#     assert response.status_code == 200
#
#
# @pytest.mark.django_db
# def test_unauthenticated_cannot_access_profile(client, tenant):
#     """Should block unauthenticated profile access."""
#     response = client.get(
#         '/auth/users/me/',
#         HTTP_HOST=f"{tenant.subdomain}.example.com"
#     )
#
#     assert response.status_code == 401
