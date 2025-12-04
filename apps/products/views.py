from rest_framework import viewsets, filters
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination

from rest_framework.permissions import AllowAny
from .models import Product, Variant
from .serializers import ProductSerializer, ProductCreateSerializer, VariantSerializer, VariantSerializerWithProduct


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


class ProductViewSet(viewsets.ModelViewSet):

    queryset = Product.objects.select_related(
        "company", "shop").prefetch_related("variants").all()
    permission_classes = [AllowAny,]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "description", "company__name"]
    ordering_fields = ["id", "title"]
    ordering = ["-id"]
    pagination_class = StandardResultsSetPagination

    """
    Uses ProductCreateSerializer for write (create/update), ProductSerializer for reads.
    Overrides create() to return:
      - 201 Created if product was created
      - 200 OK if product existed (and possibly new variants were added)
    """

    queryset = Product.objects.select_related(
        "company", "shop").prefetch_related("variants").all()

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return ProductCreateSerializer
        return ProductSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # Save returns the product instance; serializer will have ._created attribute set inside create()
        product = serializer.save()

        # Decide status code: created if product newly created, else 200 OK
        created_flag = getattr(serializer, "_created", True)
        # Optionally examine whether any variants were added:
        variants_added = getattr(serializer, "_added_variants", False)

        read_serializer = ProductSerializer(
            product, context={"request": request})
        if created_flag:
            return Response(read_serializer.data, status=status.HTTP_201_CREATED)
        # product existed: return 200 OK (variants may or may not have been added)
        return Response(
            {
                "product": read_serializer.data,
                "info": "product existed; variants added" if variants_added else "product and variants already existed; nothing changed"
            },
            status=status.HTTP_200_OK
        )


class VariantViewSet(viewsets.ModelViewSet):
    queryset = Variant.objects.select_related(
        "product").all()
    serializer_class = VariantSerializerWithProduct
    permission_classes = [AllowAny,]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["history_status", "product__title"]
    ordering_fields = ["id", "history_status"]
    ordering = ["-id"]
