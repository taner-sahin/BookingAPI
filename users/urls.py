from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import RegisterViewSet

app_name = "users"

router = SimpleRouter()
router.register(
    "register",
    RegisterViewSet,
    basename="register",
)

urlpatterns = [
    path("", include(router.urls)),
]
