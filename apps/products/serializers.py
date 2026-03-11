from rest_framework import serializers
from django.db import transaction
from rest_framework import serializers

from apps.shops.models import Shop
from .models import Product, Company, Variant
from rest_framework import serializers
from django.db import transaction
from .models import Product, Variant


class VariantCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Variant
        fields = ("ram", "storage", "product")

    def create(self, validated_data):
        product = validated_data['product']
        variant = Variant.objects.create(
            product=product, ram=validated_data['ram'], storage=validated_data['storage']
        )
        return variant


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

        product_qs = Product.actives.filter(
            shop=shop, company=company, title__iexact=title)
        product = product_qs.first()

        if product is None:
            # product doesn't exist -> create it and all variants
            product = Product.actives.create(**validated_data)
            for v in variants_data:
                Variant.actives.get_or_create(
                    product=product,
                    ram=v["ram"],
                    storage=v["storage"],
                )
            self._created = True
            return product

        # product exists
        self._created = False
        created_any_variant = False

        for v in variants_data:
            _, created = Variant.actives.get_or_create(
                product=product,
                ram=v["ram"],
                storage=v["storage"],
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


class PhoneCreateSerializer(serializers.Serializer):
    shop = serializers.PrimaryKeyRelatedField(queryset=Shop.actives.all())
    company = serializers.CharField(max_length=250)
    model = serializers.CharField(max_length=255)
    ram = serializers.IntegerField()
    storages = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False
    )

    def validate_storages(self, value):
        if len(set(value)) != len(value):
            raise serializers.ValidationError(
                "Duplicate storage values are not allowed.")
        return value

    @transaction.atomic
    def create(self, validated_data):
        shop = validated_data["shop"]
        company_name = validated_data["company"]
        title = validated_data["model"]
        ram = validated_data["ram"]
        storages = validated_data["storages"]

        # 1️⃣ Company
        company, _ = Company.objects.get_or_create(
            name__iexact=company_name,
            defaults={"name": company_name},
        )

        # 2️⃣ Product (idempotent)
        product, _ = Product.objects.get_or_create(
            shop=shop,
            company=company,
            title__iexact=title,
            defaults={"title": title},
        )

        # 3️⃣ Variants
        variants = []
        for storage in storages:
            variant, _ = Variant.objects.get_or_create(
                product=product,
                ram=ram,
                storage=storage,
            )
            variants.append(variant)

        return product


class VariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Variant
        fields = ("id", "ram", "storage",)


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
        fields = ("id", "ram", "storage", "product")

    def get_product(self, obj):
        product = obj.product
        return {
            "id": product.id,
            "shop": product.shop.id,
            "company": product.company.id,
            "title": product.title,
            "description": product.description,
        }
