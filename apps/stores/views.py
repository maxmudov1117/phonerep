from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from .serializers import BalanceItemSerializer
from apps.documents.models import BalanceItem
from rest_framework.filters import SearchFilter
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.pagination import PageNumberPagination
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


class StoreBaseView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = BalanceItemSerializer
    queryset = BalanceItem.actives.all()
    pagination_class = StandardResultsSetPagination
    filter_backends = [SearchFilter]
    search_fields = [
        'variant__product__title',
        'variant__product__company__name',
        'variant__imeis__imei_code'
    ]


class StoreListView(StoreBaseView):
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="search",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Search across: ram, storage, product title, company name, imei code",
            ),
            OpenApiParameter(
                name="shop",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Filter by shop id",
            ),
            # Document pagination params explicitly (spectacular will document them automatically,
            # but listing them gives clearer descriptions and order in the UI)
            OpenApiParameter(
                name="page",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Page number (pagination)",
            ),
            OpenApiParameter(
                name="page_size",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Items per page (pagination). Max is controlled by `max_page_size`.",
            ),
        ],
        description="List store items with optional shop filter. Paginated response.",
        # Optionally: specify response schema if you want to force the shape;
        # drf-spectacular will automatically show paginated serializer response.
    )
    def get(self, request, *args, **kwargs):
        shop_id = request.query_params.get("shop")

        queryset = self.get_queryset()

        if shop_id:
            queryset = queryset.filter(variant__product__shop_id=shop_id)

        # apply DRF search filter backend
        queryset = self.filter_queryset(queryset)

        # apply pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
