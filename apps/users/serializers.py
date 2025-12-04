from django.contrib.auth import get_user_model, password_validation
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={
                                     "input_type": "password"})
    password2 = serializers.CharField(write_only=True, required=True, style={
                                      "input_type": "password"})

    class Meta:
        model = User
        # adjust fields to match your user model
        fields = ("id", "phone_number", "full_name", "password", "password2")
        extra_kwargs = {"phone_number": {"required": False}}

    def validate_phone_number(self, value):
        if User.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError(
                "A user with this phone number already exists.")
        return value

    def validate(self, data):
        if data["password"] != data["password2"]:
            raise serializers.ValidationError(
                {"password": "Passwords do not match."})
        # validate password rules
        password_validation.validate_password(data["password"], self.instance)
        return data

    def create(self, validated_data):
        validated_data.pop("password2", None)
        password = validated_data.pop("password")
        # create_user should exist on your user manager; if not, use User.objects.create(...)
        user = User.objects.create_user(password=password, **validated_data)
        return user


class TokenObtainPairByPhoneSerializer(serializers.Serializer):
    """
    Lightweight serializer to generate tokens after validating phone_number + password.
    We won't use simplejwt's default serializer because it expects 'username'.
    """
    phone_number = serializers.CharField(write_only=True)
    password = serializers.CharField(
        write_only=True, style={"input_type": "password"})
    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)

    def validate(self, attrs):
        phone = attrs.get("phone_number")
        password = attrs.get("password")

        try:
            user = User.objects.get(phone_number=phone)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                "No active account found with the given credentials")

        if not user.check_password(password):
            raise serializers.ValidationError(
                "No active account found with the given credentials")

        if not user.is_active:
            raise serializers.ValidationError("User account is disabled.")

        refresh = RefreshToken.for_user(user)
        user = UserSerializer(user).data
        user['access'] = str(refresh.access_token)
        user['refresh'] = str(refresh)
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "phone_number", "full_name",
                  "is_active",)  # adjust as needed
        read_only_fields = ("id", "is_active")


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(
        write_only=True, required=True, style={"input_type": "password"})
    new_password = serializers.CharField(
        write_only=True, required=True, style={"input_type": "password"})

    def validate_new_password(self, value):
        password_validation.validate_password(
            value, self.context.get("request").user)
        return value
