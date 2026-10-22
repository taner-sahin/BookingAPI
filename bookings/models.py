from django.conf import settings
from django.db import models

from resources.models import Resource


class Booking(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Bekliyor"
        CONFIRMED = "confirmed", "Onaylandı"
        CANCELLED = "cancelled", "İptal edildi"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="bookings",
    )
    resource = models.ForeignKey(
        Resource,
        on_delete=models.CASCADE,
        related_name="bookings",
    )
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.resource.name} - {self.start_time:%Y-%m-%d %H:%M}"
