from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelTest(TestCase):

    def test_create_user_with_email(self):
        # test if creating a new user using email is successful
        email = 'test@setimo.com'
        password = 'testingpass123!'

        user = get_user_model().objects.create_user(
            email=email, password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password, password)

    def test_email_normalized(self):
        # test if the email address for new user is normalized
        email = 'test@SETIMO.com'
        password = 'testingpass123!'

        user = get_user_model().objects.create_user(
            email=email, password=password
        )

        self.assertEqual(user.email, email.lower())

    def test_validation_email(self):
        # test creating user with no email raises error
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'testingpass123!')

    def test_create_superuser(self):
        # test if super user is created properly
        email = 'test@SETIMO.com'
        password = 'testingpass123!'

        user = get_user_model().objects.create_superuser(
            email=email, password=password
        )

        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
