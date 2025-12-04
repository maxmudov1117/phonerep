from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Shop

User = get_user_model()


class UserSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "full_name", "phone_number")


class ShopSerializer(serializers.ModelSerializer):
    created_by = UserSimpleSerializer(read_only=True)
    created_by_id = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=User.objects.all(), required=False, source="created_by"
    )
    admins = serializers.PrimaryKeyRelatedField(
        many=True, queryset=User.objects.all(), required=False
    )
    admins_info = UserSimpleSerializer(
        source="admins", many=True, read_only=True)

    class Meta:
        model = Shop
        fields = (
            "id",
            "name",
            "address",
            "created_by",
            "created_by_id",
            "admins",
            "admins_info",
        )
        read_only_fields = ("id", "created_by", "admins_info")

    def create(self, validated_data):
        admins = validated_data.pop("admins", [])
        created_by = validated_data.pop("created_by", None)

        request = self.context.get("request")
        if created_by is None and request is not None:
            created_by = request.user

        shop = Shop.objects.create(created_by=created_by, **validated_data)

        if admins:
            shop.admins.set(admins)
        else:
            if created_by is not None:
                shop.admins.add(created_by)

        return shop

    def update(self, instance, validated_data):
        # handle admins separately
        admins = validated_data.pop("admins", None)
        # created_by should not be changed via normal update — ignore if provided
        validated_data.pop("created_by", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if admins is not None:
            instance.admins.set(admins)
        return instance
