from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from resources.models import Resource

from .models import Booking


class BookingAPITests(APITestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(
            username="booking_tester",
            email="booking_tester@example.com",
            password="TestPass123!",
        )
        self.resource = Resource.objects.create(
            name="Test Toplantı Odası",
            capacity=5,
        )

        self.start_time = timezone.now() + timedelta(days=2)
        self.end_time = self.start_time + timedelta(hours=1)

        self.booking = Booking.objects.create(
            user=self.user,
            resource=self.resource,
            start_time=self.start_time,
            end_time=self.end_time,
        )

        self.client.force_authenticate(user=self.user)

    def test_obtain_jwt_token_pair(self):
        client = APIClient()
        response = client.post(
            "/api/token/",
            {
                "username": "booking_tester",
                "password": "TestPass123!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_unauthenticated_user_cannot_list_bookings(self):
        self.client.force_authenticate(user=None)

        response = self.client.get("/api/bookings/")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_bookings(self):
        response = self.client.get("/api/bookings/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_list_only_returns_current_users_bookings(self):
        user_model = get_user_model()
        other_user = user_model.objects.create_user(
            username="another_tester",
            email="another_tester@example.com",
            password="TestPass456!",
        )
        Booking.objects.create(
            user=other_user,
            resource=self.resource,
            start_time=self.start_time + timedelta(days=5),
            end_time=self.end_time + timedelta(days=5),
        )

        response = self.client.get("/api/bookings/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], self.booking.id)

    def test_retrieve_booking(self):
        response = self.client.get(f"/api/bookings/{self.booking.id}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.booking.id)

    def test_create_booking(self):
        new_start_time = self.start_time + timedelta(days=1)
        new_end_time = new_start_time + timedelta(hours=1)

        response = self.client.post(
            "/api/bookings/",
            {
                "resource": self.resource.id,
                "start_time": new_start_time.isoformat(),
                "end_time": new_end_time.isoformat(),
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Booking.objects.count(), 2)
        self.assertEqual(response.data["status"], Booking.Status.PENDING)
        self.assertEqual(response.data["user"], self.user.id)

    def test_user_cannot_change_booking_owner(self):
        user_model = get_user_model()
        other_user = user_model.objects.create_user(
            username="owner_change_tester",
            email="owner_change_tester@example.com",
            password="TestPass789!",
        )

        response = self.client.patch(
            f"/api/bookings/{self.booking.id}/",
            {"user": other_user.id},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["user"], self.user.id)

        self.booking.refresh_from_db()
        self.assertEqual(self.booking.user_id, self.user.id)

    def test_patch_booking_status(self):
        response = self.client.patch(
            f"/api/bookings/{self.booking.id}/",
            {"status": Booking.Status.CONFIRMED},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, Booking.Status.CONFIRMED)

    def test_put_booking(self):
        new_start_time = self.start_time + timedelta(days=1)
        new_end_time = new_start_time + timedelta(hours=1)

        response = self.client.put(
            f"/api/bookings/{self.booking.id}/",
            {
                "resource": self.resource.id,
                "start_time": new_start_time.isoformat(),
                "end_time": new_end_time.isoformat(),
                "status": Booking.Status.CONFIRMED,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["user"], self.user.id)

    def test_delete_booking(self):
        response = self.client.delete(f"/api/bookings/{self.booking.id}/")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Booking.objects.filter(id=self.booking.id).exists())

    def test_create_booking_with_invalid_resource(self):
        new_start_time = self.start_time + timedelta(days=1)
        new_end_time = new_start_time + timedelta(hours=1)

        response = self.client.post(
            "/api/bookings/",
            {
                "resource": 99999,
                "start_time": new_start_time.isoformat(),
                "end_time": new_end_time.isoformat(),
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Booking.objects.count(), 1)

    def test_create_booking_with_end_time_before_start_time(self):
        invalid_start_time = self.start_time + timedelta(days=1)
        invalid_end_time = invalid_start_time - timedelta(hours=1)

        response = self.client.post(
            "/api/bookings/",
            {
                "resource": self.resource.id,
                "start_time": invalid_start_time.isoformat(),
                "end_time": invalid_end_time.isoformat(),
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("end_time", response.data)
        self.assertEqual(Booking.objects.count(), 1)

    def test_create_booking_with_overlapping_time(self):
        overlapping_start_time = self.start_time + timedelta(minutes=30)
        overlapping_end_time = self.end_time + timedelta(minutes=30)

        response = self.client.post(
            "/api/bookings/",
            {
                "resource": self.resource.id,
                "start_time": overlapping_start_time.isoformat(),
                "end_time": overlapping_end_time.isoformat(),
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Booking.objects.count(), 1)

    def test_create_booking_with_inactive_resource(self):
        inactive_resource = Resource.objects.create(
            name="Pasif Toplantı Odası",
            capacity=5,
            is_active=False,
        )
        new_start_time = self.start_time + timedelta(days=1)
        new_end_time = new_start_time + timedelta(hours=1)

        response = self.client.post(
            "/api/bookings/",
            {
                "resource": inactive_resource.id,
                "start_time": new_start_time.isoformat(),
                "end_time": new_end_time.isoformat(),
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Booking.objects.count(), 1)
