from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class RegisterAPITests(APITestCase):
    def setUp(self):
        self.url = reverse("users:register-list")
        self.valid_data = {
            "username": "booking_test_user",
            "email": "booking_test@example.com",
            "password": "Nehir!47Bulut#92",
            "password2": "Nehir!47Bulut#92",
        }

    def test_anonymous_user_can_register(self):
        response = self.client.post(self.url, self.valid_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(username=self.valid_data["username"])
        self.assertEqual(user.email, self.valid_data["email"])
        self.assertEqual(response.data["id"], user.pk)

    def test_password_fields_are_not_in_response(self):
        response = self.client.post(self.url, self.valid_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertNotIn("password", response.data)
        self.assertNotIn("password2", response.data)

    def test_password_is_hashed(self):
        response = self.client.post(self.url, self.valid_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(username=self.valid_data["username"])
        self.assertNotEqual(user.password, self.valid_data["password"])
        self.assertTrue(user.check_password(self.valid_data["password"]))

    def test_mismatched_passwords_are_rejected(self):
        data = self.valid_data.copy()
        data["password2"] = "Farkli!58Deniz#73"

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password2", response.data)
        self.assertFalse(User.objects.exists())

    def test_weak_password_is_rejected(self):
        data = self.valid_data.copy()
        data["password"] = "123456"
        data["password2"] = "123456"

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(User.objects.exists())

    def test_duplicate_username_is_rejected(self):
        existing_user = User.objects.create_user(
            username=self.valid_data["username"],
            password="Mevcut!83Kaya#61",
        )

        response = self.client.post(self.url, self.valid_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("username", response.data)
        self.assertEqual(User.objects.count(), 1)
        existing_user.refresh_from_db()
        self.assertEqual(existing_user.email, "")

    def test_missing_required_fields_are_rejected(self):
        response = self.client.post(self.url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        for field in ("username", "password", "password2"):
            self.assertIn(field, response.data)
        self.assertFalse(User.objects.exists())

    def test_registration_cannot_grant_admin_permissions(self):
        data = self.valid_data.copy()
        data["is_staff"] = True
        data["is_superuser"] = True

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(username=data["username"])
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_get_is_not_allowed(self):
        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )
