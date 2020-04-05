from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('users:create')
CREATE_TOKEN_URL = reverse('users:token')


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
