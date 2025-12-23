from apps.documents.models import BalanceItem, Imei
from rest_framework.serializers import ModelSerializer, SerializerMethodField

from apps.providers.serializers import ProviderSerializer


class ImeiSerializer(ModelSerializer):
    class Meta:
        model = Imei
        exclude = ('deleted_at',)


class VariantSerializerForBalance(ModelSerializer):

    product = SerializerMethodField()

    class Meta:
        model = BalanceItem.variant.field.related_model
        exclude = ('deleted_at',)

    def get_product(self, obj):
        return {
            "id": obj.product.id,
            "title": obj.product.title,
            "description": obj.product.description,
        }


class BalanceItemSerializer(ModelSerializer):
    variant = SerializerMethodField()
    product = SerializerMethodField()
    imeis = ImeiSerializer(read_only=True, many=True)
    provider = ProviderSerializer(read_only=True)

    class Meta:
        model = BalanceItem
        exclude = ('deleted_at',)

    def get_variant(self, obj):
        return VariantSerializerForBalance(obj.variant).data

    def get_product(self, obj):
        product = obj.variant.product
        return {
            "id": product.id,
            "title": product.title,
            "description": product.description,
        }
