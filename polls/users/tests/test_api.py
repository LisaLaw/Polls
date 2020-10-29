from rest_framework import status
from rest_framework.test import APITestCase

from polls.users.models import User
from polls.users.tests.factories import UserFactory


class UserAPITests(APITestCase):

    def setUp(self):
        self.user = UserFactory()

    def test_list_users(self):
        UserFactory.create_batch(size=10)
        self.client.force_authenticate(self.user)
        response = self.client.get("/api/v1/users/", format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(1, data["count"])

    def test_register_user(self):
        users = User.objects.all().count()
        data = {
            "email": "new@example.com",
            "password": "some_password",
            "questions": [], #needed, but empty because a new user doesn't have any questions associated with them yet
            "choices": [],
            }
        response = self.client.post("/api/v1/users/", data=data, format="json")
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(users + 1, User.objects.all().count())
        user = User.objects.get(email=data["email"])
        self.assertTrue(user.check_password(data["password"]))

    def test_get_me(self):
        self.client.force_authenticate(self.user)
        response = self.client.get("/api/v1/users/me/", format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn("id", data)

    def test_update_me(self):
        self.client.force_authenticate(self.user)
        data = {
            "email": "client1@example.com",
            "password": "new_password",
        }
        response = self.client.patch("/api/v1/users/me/", data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user = User.objects.get(pk=self.user.pk)
        self.assertEqual(data["email"], user.email)
        self.assertTrue(user.check_password(data["password"]))


class VerifyEmailAPITests(APITestCase):

    def setUp(self):
        self.user = UserFactory()

    def test_request_restore_code(self):
        self.user.is_email_verified = False
        self.user.save()
        self.assertFalse(self.user.is_email_verified)
        data = {
            "verification_code": self.user.verification_code,
        }
        response = self.client.post(
            "/api/v1/verify_email/",
            data=data,
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(pk=self.user.pk)
        self.assertTrue(user.is_email_verified)


class RestorePasswordAPITests(APITestCase):

    def setUp(self):
        self.user = UserFactory()

    def test_request_restore_code(self):
        self.assertIsNone(self.user.restore_password_code)
        data = {
            "email": self.user.email,
        }
        response = self.client.post(
            "/api/v1/request_restore_code/",
            data=data,
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(pk=self.user.pk)
        self.assertIsNotNone(user.restore_password_code)

    def test_restore_password(self):
        self.user.send_restore_code()
        data = {
            "password": "new_password",
            "repeat_password": "new_password",
            "restore_password_code": self.user.restore_password_code,
        }
        response = self.client.post(
            "/api/v1/restore_password/",
            data=data,
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(pk=self.user.pk)
        self.assertTrue(user.check_password(data["password"]))