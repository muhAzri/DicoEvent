from rest_framework import serializers
from django.contrib.auth import authenticate, get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ("id", "username", "email", "password")

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email already exists")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"], 
            email=validated_data["email"],
            password=validated_data["password"]
        )
        return user

    def to_representation(self, instance):
        return {"id": str(instance.id), "username": instance.username, "email": instance.email}


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        username = attrs.get("username")
        password = attrs.get("password")

        if username and password:
            user = authenticate(username=username, password=password)
            if user:
                attrs["user"] = user
                return attrs
            else:
                raise serializers.ValidationError("Invalid username or password")
        else:
            raise serializers.ValidationError("Must include username and password")

    def create(self, validated_data):
        user = validated_data["user"]
        refresh = RefreshToken.for_user(user)

        # Add user info to token payload
        refresh["is_admin"] = user.is_admin
        refresh["is_superuser"] = user.is_superuser
        access = refresh.access_token
        access["is_admin"] = user.is_admin
        access["is_superuser"] = user.is_superuser

        return {
            "refresh": str(refresh),
            "access": str(access),
        }


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "created_at", "updated_at")

    def to_representation(self, instance):
        return {
            "id": str(instance.id),
            "username": instance.username,
            "is_admin": instance.is_admin,
            "is_superuser": instance.is_superuser,
            "groups": [group.name for group in instance.groups.all()],
            "created_at": instance.created_at.isoformat(),
            "updated_at": instance.updated_at.isoformat(),
        }


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email", "first_name", "last_name")

    def to_representation(self, instance):
        return {
            "id": str(instance.id),
            "username": instance.username or "",
            "email": instance.email or "",
            "first_name": instance.first_name or "",
            "last_name": instance.last_name or "",
        }


class UserUpdateSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ("username", "password")

    def validate_username(self, value):
        user = self.instance
        if User.objects.exclude(pk=user.pk).filter(username=value).exists():
            raise serializers.ValidationError("Username already exists")
        return value

    def update(self, instance, validated_data):
        instance.username = validated_data.get("username", instance.username)
        if "password" in validated_data:
            instance.set_password(validated_data["password"])
        instance.save()
        return instance
