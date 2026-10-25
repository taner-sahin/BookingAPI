from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

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

    def test_list_bookings(self):
        response = self.client.get("/api/bookings/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

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
                "user": self.user.id,
                "resource": self.resource.id,
                "start_time": new_start_time.isoformat(),
                "end_time": new_end_time.isoformat(),
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Booking.objects.count(), 2)
        self.assertEqual(response.data["status"], Booking.Status.PENDING)

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
                "user": self.user.id,
                "resource": self.resource.id,
                "start_time": new_start_time.isoformat(),
                "end_time": new_end_time.isoformat(),
                "status": Booking.Status.CONFIRMED,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

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
                "user": self.user.id,
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
                "user": self.user.id,
                "resource": self.resource.id,
                "start_time": invalid_start_time.isoformat(),
                "end_time": invalid_end_time.isoformat(),
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("end_time", response.json())
        self.assertEqual(Booking.objects.count(), 1)

    def test_create_booking_with_overlapping_time(self):
        overlapping_start_time = self.start_time + timedelta(minutes=30)
        overlapping_end_time = self.end_time + timedelta(minutes=30)

        response = self.client.post(
            "/api/bookings/",
            {
                "user": self.user.id,
                "resource": self.resource.id,
                "start_time": overlapping_start_time.isoformat(),
                "end_time": overlapping_end_time.isoformat(),
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Booking.objects.count(), 1)
