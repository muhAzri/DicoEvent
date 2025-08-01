from rest_framework import serializers
from django.contrib.auth import authenticate, get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'password')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            role='user'
        )
        return user

    def to_representation(self, instance):
        return {
            'id': str(instance.id),
            'username': instance.username
        }


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if user:
                attrs['user'] = user
                return attrs
            else:
                raise serializers.ValidationError('Invalid username or password')
        else:
            raise serializers.ValidationError('Must include username and password')

    def create(self, validated_data):
        user = validated_data['user']
        refresh = RefreshToken.for_user(user)
        
        # Add role to token payload
        refresh['role'] = user.role
        access = refresh.access_token
        access['role'] = user.role
        
        return {
            'refresh': str(refresh),
            'access': str(access),
        }


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'role', 'created_at', 'updated_at')
        
    def to_representation(self, instance):
        return {
            'id': str(instance.id),
            'username': instance.username,
            'role': instance.role,
            'created_at': instance.created_at.isoformat(),
            'updated_at': instance.updated_at.isoformat(),
        }


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')
        
    def to_representation(self, instance):
        return {
            'username': instance.username or '',
            'email': instance.email or '',
            'first_name': instance.first_name or '',
            'last_name': instance.last_name or '',
        }