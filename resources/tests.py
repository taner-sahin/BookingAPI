from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Resource


class ResourceAPITests(APITestCase):
    def setUp(self):
        self.list_url = reverse("resources:resource-list")

        self.resource = Resource.objects.create(
            name="Test Toplantı Odası",
            description="Otomatik test için.",
            capacity=6,
            is_active=True,
        )

    def test_list_resources(self):
        Resource.objects.create(
            name="Pasif Eğitim Salonu",
            description="Pasif kaynak testi.",
            capacity=20,
            is_active=False,
        )

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertIn(
            "Pasif Eğitim Salonu",
            [item["name"] for item in response.data],
        )

    def test_retrieve_resource(self):
        url = reverse(
            "resources:resource-detail",
            kwargs={"pk": self.resource.pk},
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Test Toplantı Odası")

    def test_create_resource(self):
        data = {
            "name": "Yeni Test Odası",
            "description": "API ile oluşturuldu.",
            "capacity": 10,
            "is_active": True,
        }

        response = self.client.post(self.list_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Resource.objects.filter(name="Yeni Test Odası").exists())

    def test_reject_zero_capacity(self):
        data = {
            "name": "Geçersiz Oda",
            "description": "Kapasite sıfır olamaz.",
            "capacity": 0,
            "is_active": True,
        }

        response = self.client.post(self.list_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(Resource.objects.filter(name="Geçersiz Oda").exists())

    def test_partial_update_resource(self):
        url = reverse(
            "resources:resource-detail",
            kwargs={"pk": self.resource.pk},
        )

        response = self.client.patch(
            url,
            {"capacity": 8},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.resource.refresh_from_db()
        self.assertEqual(self.resource.capacity, 8)
        self.assertEqual(self.resource.name, "Test Toplantı Odası")

    def test_replace_resource(self):
        url = reverse(
            "resources:resource-detail",
            kwargs={"pk": self.resource.pk},
        )
        data = {
            "name": "Güncellenmiş Oda",
            "description": "Tam güncelleme testi.",
            "capacity": 15,
            "is_active": False,
        }

        response = self.client.put(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.resource.refresh_from_db()
        self.assertEqual(self.resource.name, "Güncellenmiş Oda")
        self.assertEqual(self.resource.capacity, 15)
        self.assertFalse(self.resource.is_active)

    def test_delete_resource(self):
        url = reverse(
            "resources:resource-detail",
            kwargs={"pk": self.resource.pk},
        )

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Resource.objects.filter(pk=self.resource.pk).exists())
