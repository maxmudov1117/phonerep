from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from .models import Provider
from .serializers import ProviderSerializer, CreateProviderSerializer


class ProviderViewSet(ModelViewSet):
    queryset = Provider.objects.all()
    permission_classes = (IsAuthenticated,)

    # def get_serializer_class(self):
    #     if self.request.method == "GET":
    #         return ProviderListSerializer   # for list + retrieve
    #     elif self.request.method == "POST":
    #         return ProviderCreateSerializer # for create
    #     elif self.request.method in ("PUT", "PATCH"):
    #         return ProviderUpdateSerializer # for update
    #     return ProviderSerializer          # fallback

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CreateProviderSerializer
        return ProviderSerializer
