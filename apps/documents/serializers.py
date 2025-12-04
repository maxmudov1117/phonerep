from rest_framework import serializers
from .models import Document


class DocumentSerializer(serializers.ModelSerializer):
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Document
        exclude = ["deleted_at",]

    def get_total_price(self, obj: Document):
        items = obj.documentitem_set.all()
        total = sum([item.income_price * item.qty for item in items])
        return total


class ProductItemSerializer(serializers.Serializer):
    variant_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)
    history_status = serializers.CharField(required=False, allow_blank=True)
    income_price = serializers.DecimalField(
        max_digits=20, decimal_places=2, required=False)
    imei_codes = serializers.ListField(
        child=serializers.CharField(), required=False
    )


class BuySerializer(serializers.Serializer):
    items = ProductItemSerializer(many=True)
    discount = serializers.DecimalField(
        max_digits=10, decimal_places=2, required=False)


class SellItemSerializer(serializers.Serializer):
    variant_id = serializers.IntegerField()
    qty = serializers.IntegerField(min_value=1)


class SellSerializer(serializers.Serializer):
    items = SellItemSerializer(many=True)
    discount = serializers.DecimalField(
        max_digits=10, decimal_places=2, required=False)
