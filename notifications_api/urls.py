from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import DistributionViewSet, ClientViewSet, MessageViewSet
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)


router = SimpleRouter()
router.register("distributions", DistributionViewSet, basename="Distribution")
router.register("clients", ClientViewSet)
router.register("messages", MessageViewSet)


urlpatterns = [
    path("auth/", include("rest_framework.urls")),
    path("v1/", include(router.urls)),
    path("v1/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "v1/schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "v1/schema/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
]
