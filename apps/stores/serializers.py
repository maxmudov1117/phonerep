from apps.documents.models import BalanceItem
from rest_framework.serializers import ModelSerializer, SerializerMethodField


class VariantSerializerForBalance(ModelSerializer):
    product = SerializerMethodField()

    class Meta:
        model = BalanceItem.variant.field.related_model
        fields = "__all__"

    def get_product(self, obj):
        return {
            "id": obj.product.id,
            "title": obj.product.title,
            "description": obj.product.description,
        }


class BalanceItemSerializer(ModelSerializer):
    variant = SerializerMethodField()
    product = SerializerMethodField()
    imeies = SerializerMethodField()

    class Meta:
        model = BalanceItem
        fields = "__all__"

    def get_variant(self, obj):
        return VariantSerializerForBalance(obj.variant).data

    def get_imeies(self, obj):
        imeies = obj.variant.imeis.all()
        return [{"id": imei.id, "imei_code": imei.imei_code} for imei in imeies]

    def get_product(self, obj):

        product = obj.variant.product
        return {
            "id": product.id,
            "title": product.title,
            "description": product.description,
        }
