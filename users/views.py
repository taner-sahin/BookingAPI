from typing import ClassVar

from rest_framework import mixins, viewsets
from rest_framework.permissions import AllowAny

from .serializers import RegisterSerializer


class RegisterViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = RegisterSerializer
    permission_classes = (AllowAny,)
    http_method_names: ClassVar[list[str]] = ["post", "options"]
