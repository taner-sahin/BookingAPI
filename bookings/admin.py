from django.contrib import admin

from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "resource",
        "start_time",
        "end_time",
        "status",
        "created_at",
    )
    list_filter = ("status", "resource")
    search_fields = ("user__username", "resource__name")
    readonly_fields = ("created_at",)
