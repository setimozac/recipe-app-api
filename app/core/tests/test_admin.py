from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse


class AdminSiteTest(TestCase):

    def setUp(self):
        self.client = Client()
        email = "testadmin@setimo.com"
        password = "testingpass123!"
        self.superuser = get_user_model().objects.create_superuser(
            email=email, password=password
        )

        self.client.force_login(self.superuser)

        self.user = get_user_model().objects.create_user(
            email="testuser1@setimo.com",
            password="testpass123!",
            name="testuser1"
        )

    def test_adminpage_listed_users(self):
        # test that all the users are listed in the user page
        url = reverse("admin:core_user_changelist")
        res = self.client.get(url)

        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)

    def test_user_change_page(self):
        # test that user edit page works
        url = reverse("admin:core_user_change", args=[self.user.id])
        # print(url)
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

    def test_user_add_page(self):
        # test create user page functionality
        url = reverse("admin:core_user_add")
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
