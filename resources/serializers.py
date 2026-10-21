from rest_framework import serializers

from .models import Resource


class ResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resource
        fields = (
            "id",
            "name",
            "description",
            "capacity",
            "is_active",
            "created_at",
        )
        read_only_fields = ("id", "created_at")
