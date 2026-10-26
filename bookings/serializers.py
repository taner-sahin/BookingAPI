from rest_framework import serializers

from .models import Booking


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = (
            "id",
            "user",
            "resource",
            "start_time",
            "end_time",
            "status",
            "created_at",
        )

        read_only_fields = ("id", "created_at", "user")

    def validate(self, attrs):
        start_time = attrs.get(
            "start_time",
            getattr(self.instance, "start_time", None),
        )
        end_time = attrs.get(
            "end_time",
            getattr(self.instance, "end_time", None),
        )
        resource = attrs.get(
            "resource",
            getattr(self.instance, "resource", None),
        )

        reservation_details_changed = self.instance is None or any(
            field in attrs for field in ("resource", "start_time", "end_time")
        )

        if resource and reservation_details_changed and not resource.is_active:
            raise serializers.ValidationError(
                {"resource": "Pasif bir kaynak için rezervasyon yapılamaz."}
            )

        if start_time and end_time and end_time <= start_time:
            raise serializers.ValidationError(
                {"end_time": "Bitiş zamanı başlangıç zamanından sonra olmalıdır."}
            )

        if start_time and end_time and resource:
            overlapping_bookings = Booking.objects.filter(
                resource=resource,
                start_time__lt=end_time,
                end_time__gt=start_time,
            ).exclude(status=Booking.Status.CANCELLED)

            if self.instance:
                overlapping_bookings = overlapping_bookings.exclude(pk=self.instance.pk)

            if overlapping_bookings.exists():
                raise serializers.ValidationError(
                    "Bu kaynak seçilen saat aralığında zaten rezerve edilmiş."
                )

        return attrs
