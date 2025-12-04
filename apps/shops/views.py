from django.shortcuts import get_object_or_404, render

# Create your views here.
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny
from rest_framework import filters
from rest_framework.pagination import PageNumberPagination
from apps.products.models import Product

from .models import Shop
from .serializers import ShopSerializer
from .permissions import IsShopOwnerOrAdminOrReadOnly


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


class ShopViewSet(viewsets.ModelViewSet):
    """
    endpoints:
      GET    /api/shops/           -> list
      POST   /api/shops/           -> create
      GET    /api/shops/{pk}/      -> retrieve
      PUT    /api/shops/{pk}/      -> update
      PATCH  /api/shops/{pk}/      -> partial_update
      DELETE /api/shops/{pk}/      -> destroy
      POST   /api/shops/{pk}/add_admin/    -> custom action to add admin(s)
      POST   /api/shops/{pk}/remove_admin/ -> custom action to remove admin(s)
    """

    queryset = Shop.objects.all().prefetch_related("admins")
    serializer_class = ShopSerializer
    permission_classes = (IsShopOwnerOrAdminOrReadOnly,)
    # filter_backends = (DjangoFilterBackend,
    #                    filters.SearchFilter, filters.OrderingFilter)
    # allow filtering by creator/admin/id/name
    filterset_fields = ("created_by", "admins", "name")
    search_fields = ("name", "address")
    ordering_fields = ("name", "id")
    ordering = ("-id",)

    def perform_create(self, serializer):
        # set created_by to request.user always (more secure)
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=["post"], url_path="add_admin", permission_classes=[IsShopOwnerOrAdminOrReadOnly])
    def add_admin(self, request, pk=None):
        """
        Add one or multiple users to shop.admins.
        Payload: {"admins": [user_id1, user_id2]}
        """
        shop = self.get_object()
        # permission checked by object permission
        user_ids = request.data.get("admins", [])
        if not isinstance(user_ids, (list, tuple)):
            return Response({"detail": "admins must be a list of user ids."}, status=status.HTTP_400_BAD_REQUEST)

        # bulk add: ignore invalid ids
        from django.contrib.auth import get_user_model
        User = get_user_model()
        users = User.objects.filter(pk__in=user_ids)
        if not users:
            return Response({"detail": "No valid users found to add."}, status=status.HTTP_400_BAD_REQUEST)

        shop.admins.add(*users)
        shop.save()
        return Response({"detail": f"Added {users.count()} admin(s)."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="remove_admin", permission_classes=[IsShopOwnerOrAdminOrReadOnly])
    def remove_admin(self, request, pk=None):
        """
        Remove one or multiple users from shop.admins.
        Payload: {"admins": [user_id1, user_id2]}
        """
        shop = self.get_object()
        user_ids = request.data.get("admins", [])
        if not isinstance(user_ids, (list, tuple)):
            return Response({"detail": "admins must be a list of user ids."}, status=status.HTTP_400_BAD_REQUEST)

        from django.contrib.auth import get_user_model
        User = get_user_model()
        users = User.objects.filter(pk__in=user_ids)
        if not users:
            return Response({"detail": "No valid users found to remove."}, status=status.HTTP_400_BAD_REQUEST)

        shop.admins.remove(*users)
        shop.save()
        return Response({"detail": f"Removed {users.count()} admin(s)."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"], permission_classes=[IsAuthenticatedOrReadOnly])
    def products(self, request, pk=None):
        from apps.products.serializers import ProductSerializer
        """
        GET /api/shops/{pk}/products/
        Returns products for the shop if the requester is allowed.
        """
        shop = get_object_or_404(Shop, pk=pk)

        # enforce object permission — reuse your permission logic
        self.check_object_permissions(request, shop)

        qs = Product.objects.filter(shop=shop).select_related(
            "company").prefetch_related("variants")

        # optional: allow filtering via query params
        ram = request.query_params.getlist("ram")
        storage = request.query_params.getlist("storage")
        if ram:
            qs = qs.filter(variants__ram__in=[int(x)
                           for x in ram if x.isdigit()]).distinct()
        if storage:
            qs = qs.filter(variants__storage__in=[
                           int(x) for x in storage if x.isdigit()]).distinct()

        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(qs, request)
        serializer = ProductSerializer(
            page, many=True, context={"request": request})
        return paginator.get_paginated_response(serializer.data)

    @action(detail=True, methods=["get"],  permission_classes=[AllowAny])
    def documents(self, request, pk=None):
        from apps.documents.serializers import DocumentSerializer
        """
        GET /api/shops/{pk}/documents/
        Returns documents for the shop if the requester is allowed. 
        """

        shop = get_object_or_404(Shop, pk=pk)
        documents = shop.documents.all().select_related("created_by")
        serializer = DocumentSerializer(
            documents, many=True,
            context={"request": request}
        )

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"],  permission_classes=[AllowAny])
    def providers(self, request, pk=None):
        from apps.providers.serializers import ProviderSerializer
        """
        GET /api/shops/{pk}/documents/
        Returns documents for the shop if the requester is allowed. 
        """

        shop = get_object_or_404(Shop, pk=pk)
        documents = shop.providers.all().select_related("created_by")
        serializer = ProviderSerializer(
            documents, many=True,
            context={"request": request}
        )

        return Response(serializer.data, status=status.HTTP_200_OK)
