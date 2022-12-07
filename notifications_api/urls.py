from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import DistributionViewSet, ClientViewSet, MessageViewSet

router = SimpleRouter()
router.register("distributions", DistributionViewSet, basename="Distribution")
router.register("clients", ClientViewSet)
router.register("messages", MessageViewSet)


urlpatterns = [
    path("auth/", include("rest_framework.urls")),
    path("v1/", include(router.urls)),
]
