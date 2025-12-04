from rest_framework import serializers
from django.db import transaction
from rest_framework import serializers
from .models import Product, Company, Variant
from rest_framework import serializers
from django.db import transaction
from .models import Product, Variant


class VariantCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Variant
        fields = ("ram", "storage", "history_status")


class ProductCreateSerializer(serializers.ModelSerializer):
    variants = VariantCreateSerializer(many=True, required=False)

    class Meta:
        model = Product
        fields = ("id", "shop", "company", "title", "description", "variants")
        read_only_fields = ("id",)

    def validate(self, attrs):
        # optional: ensure company belongs to shop
        shop = attrs.get("shop")
        company = attrs.get("company")
        # if shop and company and getattr(company, "shop_id", None) != shop.id:
        #     raise serializers.ValidationError(
        #         {"company": "Company must belong to the selected shop."})
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        """
        Behavior:
          - If product doesn't exist -> create product + all variants (self._created = True)
          - If product exists -> create any missing variants (self._created = False)
        We set self._created to let the view decide response status code.
        """
        variants_data = validated_data.pop("variants", [])

        # Try to get existing product by exact shop/company/title match.
        # Use case-insensitive title check if you prefer: title__iexact=...
        shop = validated_data["shop"]
        company = validated_data["company"]
        title = validated_data["title"]

        product_qs = Product.objects.filter(
            shop=shop, company=company, title__iexact=title)
        product = product_qs.first()

        if product is None:
            # product doesn't exist -> create it and all variants
            product = Product.objects.create(**validated_data)
            for v in variants_data:
                Variant.objects.get_or_create(
                    product=product,
                    ram=v["ram"],
                    storage=v["storage"],
                    defaults={"history_status": v.get("history_status", "")}
                )
            self._created = True
            return product

        # product exists
        self._created = False
        created_any_variant = False

        for v in variants_data:
            _, created = Variant.objects.get_or_create(
                product=product,
                ram=v["ram"],
                storage=v["storage"],
                defaults={"history_status": v.get("history_status", "")}
            )
            if created:
                created_any_variant = True

        # Optionally update description if different — uncomment if desired:
        # new_description = validated_data.get("description")
        # if new_description and product.description != new_description:
        #     product.description = new_description
        #     product.save(update_fields=["description"])

        # Attach a flag so viewset knows whether any variant was added.
        # (serializer._created already indicates product creation; store variant flag separately)
        self._added_variants = created_any_variant

        return product


class VariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Variant
        fields = ("id", "ram", "storage", "history_status")


class ProductSerializer(serializers.ModelSerializer):
    variants = VariantSerializer(many=True, read_only=True)
    company_name = serializers.CharField(source="company.name", read_only=True)

    class Meta:
        model = Product
        fields = (
            "id",
            "shop",
            "company",
            "company_name",
            "title",
            "description",
            "variants",
        )


class VariantSerializerWithProduct(serializers.ModelSerializer):
    product = serializers.SerializerMethodField()

    class Meta:
        model = Variant
        fields = ("id", "ram", "storage", "history_status", "product")

    def get_product(self, obj):
        product = obj.product
        return {
            "id": product.id,
            "shop": product.shop.id,
            "company": product.company.id,
            "title": product.title,
            "description": product.description,
        }
