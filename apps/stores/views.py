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
    queryset = BalanceItem.objects.all()
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
                description=(
                    "Search across: ram, storage, product title, company name, imei code"
                ),
            )
        ],
        description="List store items with optional search filter.",
    )
    def get(self, request, *args, **kwargs):
        # allow filtering / ordering hooks if you add them later
        queryset = self.filter_queryset(self.get_queryset())

        # apply pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        # fallback: no pagination configured or pagination returned None
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
