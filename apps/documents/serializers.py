from decimal import Decimal
from rest_framework import serializers
from .models import Document, DocumentItem, Imei
from apps.products.serializers import VariantSerializerWithProduct


class ImeiSerializer(serializers.ModelSerializer):
    class Meta:
        model = Imei
        fields = "__all__"


class DocumentSerializer(serializers.ModelSerializer):
    total_price = serializers.SerializerMethodField()
    currency_rate = serializers.SerializerMethodField()

    class Meta:
        model = Document
        exclude = ["deleted_at",]

    def get_total_price(self, obj: Document):
        return obj.get_total_price()

    def get_currency_rate(self, obj: Document):
        from apps.currencies.models import Currency
        latest = Currency.actives.order_by(
            '-created_at').filter(shop=obj.shop).first()
        if latest is None:
            return Decimal('0.0')
        return latest.rate


class ProductItemSerializer(serializers.Serializer):
    variant_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)
    history_status = serializers.CharField(required=False, allow_blank=True)
    income_price = serializers.DecimalField(
        max_digits=20, decimal_places=2, required=False)
    imei_codes = serializers.ListField(
        child=serializers.CharField(), required=False
    )
    provider_id = serializers.IntegerField()


class BuySerializer(serializers.Serializer):
    items = ProductItemSerializer(many=True)
    discount = serializers.DecimalField(
        max_digits=10, decimal_places=2, required=False)


class SellItemSerializer(serializers.Serializer):
    balance_id = serializers.IntegerField()
    sale_price = serializers.DecimalField(max_digits=20, decimal_places=2)


class SellSerializer(serializers.Serializer):
    items = SellItemSerializer(many=True)


class DocumentItemSerializer(serializers.ModelSerializer):
    variant = VariantSerializerWithProduct()
    imeis = ImeiSerializer(many=True)

    class Meta:
        model = DocumentItem
        fields = "__all__"
