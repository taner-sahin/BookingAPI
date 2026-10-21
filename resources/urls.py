from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import ResourceViewSet

app_name = "resources"

router = SimpleRouter()
router.register("resources", ResourceViewSet, basename="resource")

urlpatterns = [
    path("", include(router.urls)),
]
