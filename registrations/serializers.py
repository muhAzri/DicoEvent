from rest_framework import serializers
from django.contrib.auth import get_user_model
from tickets.models import Ticket
from .models import Registration

User = get_user_model()


class RegistrationCreateSerializer(serializers.ModelSerializer):
    ticket_id = serializers.UUIDField(write_only=True)
    user_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = Registration
        fields = ["ticket_id", "user_id"]

    def validate_ticket_id(self, value):
        try:
            Ticket.objects.get(id=value)
            return value
        except Ticket.DoesNotExist:
            raise serializers.ValidationError("Ticket not found.")

    def validate_user_id(self, value):
        try:
            User.objects.get(id=value)
            return value
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found.")

    def validate(self, attrs):
        ticket_id = attrs["ticket_id"]
        user_id = attrs["user_id"]

        # Check if registration already exists
        if Registration.objects.filter(ticket_id=ticket_id, user_id=user_id).exists():
            raise serializers.ValidationError(
                "User is already registered for this ticket."
            )

        return attrs

    def create(self, validated_data):
        ticket_id = validated_data.pop("ticket_id")
        user_id = validated_data.pop("user_id")

        ticket = Ticket.objects.get(id=ticket_id)
        user = User.objects.get(id=user_id)

        registration = Registration.objects.create(ticket=ticket, user=user)
        return registration

    def to_representation(self, instance):
        return {
            "id": str(instance.id),
            "ticket": instance.ticket.name,
            "user": instance.user.username,
        }


class RegistrationListSerializer(serializers.ModelSerializer):
    ticket = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()
    event = serializers.SerializerMethodField()

    class Meta:
        model = Registration
        fields = ["id", "ticket", "user", "event", "created_at", "updated_at"]

    def get_ticket(self, obj):
        return {
            "id": str(obj.ticket.id),
            "name": obj.ticket.name,
            "price": float(obj.ticket.price),
        }

    def get_user(self, obj):
        return {"id": str(obj.user.id), "username": obj.user.username}

    def get_event(self, obj):
        return {"id": str(obj.ticket.event.id), "name": obj.ticket.event.name}

    def to_representation(self, instance):
        return {
            "id": str(instance.id),
            "ticket": self.get_ticket(instance),
            "user": self.get_user(instance),
            "event": self.get_event(instance),
            "created_at": instance.created_at.isoformat(),
            "updated_at": instance.updated_at.isoformat(),
        }


class RegistrationUpdateSerializer(serializers.ModelSerializer):
    ticket_id = serializers.UUIDField(write_only=True)
    user_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = Registration
        fields = ["ticket_id", "user_id"]

    def validate_ticket_id(self, value):
        try:
            Ticket.objects.get(id=value)
            return value
        except Ticket.DoesNotExist:
            raise serializers.ValidationError("Ticket not found.")

    def validate_user_id(self, value):
        try:
            User.objects.get(id=value)
            return value
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found.")

    def validate(self, attrs):
        ticket_id = attrs["ticket_id"]
        user_id = attrs["user_id"]

        # Check if registration already exists for different registration
        existing_registration = Registration.objects.filter(
            ticket_id=ticket_id, user_id=user_id
        ).exclude(id=self.instance.id if self.instance else None)

        if existing_registration.exists():
            raise serializers.ValidationError(
                "User is already registered for this ticket."
            )

        return attrs

    def update(self, instance, validated_data):
        ticket_id = validated_data.pop("ticket_id", None)
        user_id = validated_data.pop("user_id", None)

        if ticket_id:
            ticket = Ticket.objects.get(id=ticket_id)
            instance.ticket = ticket

        if user_id:
            user = User.objects.get(id=user_id)
            instance.user = user

        instance.save()
        return instance


class RegistrationDetailSerializer(serializers.ModelSerializer):
    ticket = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()
    event = serializers.SerializerMethodField()

    class Meta:
        model = Registration
        fields = ["id", "ticket", "user", "event", "created_at", "updated_at"]

    def get_ticket(self, obj):
        return obj.ticket.name

    def get_user(self, obj):
        return obj.user.username

    def get_event(self, obj):
        return obj.ticket.event.name

    def to_representation(self, instance):
        return {
            "id": str(instance.id),
            "ticket": self.get_ticket(instance),
            "user": self.get_user(instance),
            "event": self.get_event(instance),
            "created_at": instance.created_at.isoformat(),
            "updated_at": instance.updated_at.isoformat(),
        }


class RegistrationUpdateSerializer(serializers.ModelSerializer):
    ticket_id = serializers.UUIDField(write_only=True)
    user_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = Registration
        fields = ["ticket_id", "user_id"]

    def validate_ticket_id(self, value):
        try:
            Ticket.objects.get(id=value)
            return value
        except Ticket.DoesNotExist:
            raise serializers.ValidationError("Ticket not found.")

    def validate_user_id(self, value):
        try:
            User.objects.get(id=value)
            return value
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found.")

    def validate(self, attrs):
        ticket_id = attrs["ticket_id"]
        user_id = attrs["user_id"]

        # Check if registration already exists for different registration
        existing_registration = Registration.objects.filter(
            ticket_id=ticket_id, user_id=user_id
        ).exclude(id=self.instance.id if self.instance else None)

        if existing_registration.exists():
            raise serializers.ValidationError(
                "User is already registered for this ticket."
            )

        return attrs

    def update(self, instance, validated_data):
        ticket_id = validated_data.pop("ticket_id", None)
        user_id = validated_data.pop("user_id", None)

        if ticket_id:
            ticket = Ticket.objects.get(id=ticket_id)
            instance.ticket = ticket

        if user_id:
            user = User.objects.get(id=user_id)
            instance.user = user

        instance.save()
        return instance
