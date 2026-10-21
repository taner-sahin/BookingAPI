from django.core.validators import MinValueValidator
from django.db import models


class Resource(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    capacity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
