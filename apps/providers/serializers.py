from rest_framework import serializers
from .models import Provider
from apps.shops.models import Shop


class CreateProviderSerializer(serializers.Serializer):
    shop = serializers.PrimaryKeyRelatedField(queryset=Shop.objects.all())
    name = serializers.CharField(max_length=250)

    def validate(self, attrs):
        shop = attrs.get("shop")
        name = attrs.get("name")

        if Provider.objects.filter(shop=shop, name=name).exists():
            raise serializers.ValidationError(
                {"name": "Provider with this name already exists in this shop."},
            )

        return attrs

    def create(self, validated_data):
        provider = Provider.objects.create(
            shop=validated_data["shop"],
            name=validated_data["name"],
            created_by=self.context["request"].user
        )
        return provider


class ProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Provider
        fields = "__all__"
