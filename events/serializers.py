from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from PIL import Image
from .models import Event
from .services import minio_service

User = get_user_model()


class EventCreateSerializer(serializers.ModelSerializer):
    organizer_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = Event
        fields = [
            "name",
            "description",
            "location",
            "start_time",
            "end_time",
            "status",
            "quota",
            "category",
            "organizer_id",
        ]

    def validate_organizer_id(self, value):
        try:
            User.objects.get(id=value)
            return value
        except User.DoesNotExist:
            raise serializers.ValidationError("Organizer not found.")

    def create(self, validated_data):
        organizer_id = validated_data.pop("organizer_id")
        organizer = User.objects.get(id=organizer_id)
        event = Event.objects.create(organizer=organizer, **validated_data)
        return event

    def to_representation(self, instance):
        return {
            "id": str(instance.id),
            "name": instance.name,
            "description": instance.description,
            "location": instance.location,
            "start_time": instance.start_time.isoformat(),
            "end_time": instance.end_time.isoformat(),
            "status": instance.status,
            "quota": instance.quota,
            "category": instance.category,
        }


class EventListSerializer(serializers.ModelSerializer):
    organizer = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            "id",
            "name",
            "description",
            "location",
            "start_time",
            "end_time",
            "status",
            "quota",
            "category",
            "organizer",
            "created_at",
            "updated_at",
        ]

    def get_organizer(self, obj):
        return {"id": str(obj.organizer.id), "username": obj.organizer.username}

    def to_representation(self, instance):
        return {
            "id": str(instance.id),
            "name": instance.name,
            "description": instance.description,
            "location": instance.location,
            "start_time": instance.start_time.isoformat(),
            "end_time": instance.end_time.isoformat(),
            "status": instance.status,
            "quota": instance.quota,
            "category": instance.category,
            "organizer": self.get_organizer(instance),
            "created_at": instance.created_at.isoformat(),
            "updated_at": instance.updated_at.isoformat(),
        }


class EventUpdateSerializer(serializers.ModelSerializer):
    organizer_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = Event
        fields = [
            "name",
            "description",
            "location",
            "start_time",
            "end_time",
            "status",
            "quota",
            "category",
            "organizer_id",
        ]

    def validate_organizer_id(self, value):
        try:
            User.objects.get(id=value)
            return value
        except User.DoesNotExist:
            raise serializers.ValidationError("Organizer not found.")

    def update(self, instance, validated_data):
        organizer_id = validated_data.pop("organizer_id", None)
        if organizer_id:
            organizer = User.objects.get(id=organizer_id)
            instance.organizer = organizer

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class EventPosterUploadSerializer(serializers.Serializer):
    image = serializers.ImageField(required=True)
    event = serializers.UUIDField(required=True)

    def validate_image(self, value):
        """Validate image file type and size."""
        # Check file size (max 500KB)
        max_size = 500 * 1024  # 500KB in bytes
        if value.size > max_size:
            raise serializers.ValidationError(
                f"File size too large. Maximum size is 500KB. Current size: {value.size / 1024:.1f}KB"
            )

        # Check MIME type
        allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
        if value.content_type not in allowed_types:
            raise serializers.ValidationError(
                f"Invalid file type. Allowed types: {', '.join(allowed_types)}"
            )

        # Validate image using PIL
        try:
            image = Image.open(value)
            image.verify()
        except Exception as e:
            raise serializers.ValidationError("Invalid image file or corrupted image.")

        return value

    def validate_event(self, value):
        """Validate that event exists."""
        try:
            event = Event.objects.get(id=value)
            return value
        except Event.DoesNotExist:
            raise serializers.ValidationError("Event not found.")

    def create(self, validated_data):
        """Upload image to MinIO and return the result.""" 
        image = validated_data['image']
        event_id = validated_data['event']
        
        try:
            # Get the event object
            event = Event.objects.get(id=event_id)
            
            # Upload to MinIO
            filename = minio_service.upload_file(image, folder="event-posters")
            
            # Save poster filename to event
            event.poster = filename
            event.save()
            
            return {
                'id': str(event_id),
                'image': filename
            }
        except ValidationError as e:
            raise serializers.ValidationError(str(e))
        except Exception as e:
            raise serializers.ValidationError(f"Upload failed: {str(e)}")
