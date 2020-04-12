from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('users:create')
CREATE_TOKEN_URL = reverse('users:token')
MANAGE_USER_URL = reverse('users:me')


def create_user(**kwargs):
    return get_user_model().objects.create_user(**kwargs)


class PublicUserApiTest(TestCase):
    # test users API

    def setUp(self):
        self.client = APIClient()

        self.payload = {
            'email': 'testuser@something.com',
            'password': 'testingpass',
            'name': 'test user'
        }

    def test_user_create_successfull(self):
        # test creating user with valid payload

        result = self.client.post(CREATE_USER_URL, self.payload)

        self.assertEqual(result.status_code, status.HTTP_201_CREATED)

        user = get_user_model().objects.get(**result.data)
        self.assertTrue(user.check_password(self.payload['password']))
        self.assertNotIn('password', result.data)

    def test_user_exists(self):
        # test throw an error if user already exists
        create_user(**self.payload)
        result = self.client.post(CREATE_USER_URL, self.payload)

        self.assertEqual(result.status_code, status.HTTP_400_BAD_REQUEST)

    def test_short_password_fails(self):
        # password must be more then 8 characters
        payload = {
            'email': 'testuser@something.com',
            'password': 'test',
            'name': 'test user'
        }
        result = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(result.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()

        self.assertFalse(user_exists)

    def test_create_token_valid_credentials(self):

        create_user(**self.payload)
        result = self.client.post(CREATE_TOKEN_URL, self.payload)

        self.assertIn('token', result.data)
        self.assertEqual(result.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        create_user(**self.payload)
        payload = {'email': "testuser@something.com",
                   'password': "wrongpass"
                   }
        result = self.client.post(CREATE_TOKEN_URL, payload)

        self.assertEqual(result.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', result.data)

    def test_create_token_not_user(self):

        result = self.client.post(CREATE_TOKEN_URL, self.payload)

        self.assertEqual(result.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', result.data)

    def test_create_token_missing_field(self):

        create_user(**self.payload)
        del self.payload['password']
        result = self.client.post(CREATE_TOKEN_URL, self.payload)

        self.assertEqual(result.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', result.data)

    def test_manage_user_without_authentication(self):

        res = self.client.get(MANAGE_USER_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):

    def setUp(self):
        self.payload = {
            'email': 'testuser@something.com',
            'password': 'testingpass',
            'name': 'test user'
        }
        self.user = get_user_model().objects.create_user(**self.payload)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):

        res = self.client.get(MANAGE_USER_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        del self.payload['password']
        self.assertEqual(res.data, self.payload)
        self.assertEqual(res.data, {
            'name': self.user.name, 'email': self.user.email
        })

    def test_post_me_not_allowed(self):

        res = self.client.post(MANAGE_USER_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):

        self.payload['name'] = 'modified name'
        self.payload['password'] = 'modifiedpass'
        res = self.client.patch(MANAGE_USER_URL, self.payload)

        self.user.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.name, 'modified name')
        self.assertTrue(self.user.check_password('modifiedpass'))
