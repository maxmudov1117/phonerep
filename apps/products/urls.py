from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, VariantViewSet
router = DefaultRouter()
router.register(r"product", ProductViewSet, basename="product")
router.register(r"variant", VariantViewSet, basename="variant")

urlpatterns = router.urls
