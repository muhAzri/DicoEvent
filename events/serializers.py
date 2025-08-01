from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Event

User = get_user_model()


class EventCreateSerializer(serializers.ModelSerializer):
    organizer_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = Event
        fields = [
            'name', 'description', 'location', 'start_time', 'end_time', 
            'status', 'quota', 'category', 'organizer_id'
        ]
    
    def validate_organizer_id(self, value):
        try:
            User.objects.get(id=value)
            return value
        except User.DoesNotExist:
            raise serializers.ValidationError("Organizer not found.")
    
    def create(self, validated_data):
        organizer_id = validated_data.pop('organizer_id')
        organizer = User.objects.get(id=organizer_id)
        event = Event.objects.create(organizer=organizer, **validated_data)
        return event
    
    def to_representation(self, instance):
        return {
            'id': str(instance.id),
            'name': instance.name,
            'description': instance.description,
            'location': instance.location,
            'start_time': instance.start_time.isoformat(),
            'end_time': instance.end_time.isoformat(),
            'status': instance.status,
            'quota': instance.quota,
            'category': instance.category,
        }


class EventListSerializer(serializers.ModelSerializer):
    organizer = serializers.SerializerMethodField()
    
    class Meta:
        model = Event
        fields = [
            'id', 'name', 'description', 'location', 'start_time', 'end_time',
            'status', 'quota', 'category', 'organizer', 'created_at', 'updated_at'
        ]
    
    def get_organizer(self, obj):
        return {
            'id': str(obj.organizer.id),
            'username': obj.organizer.username
        }
    
    def to_representation(self, instance):
        return {
            'id': str(instance.id),
            'name': instance.name,
            'description': instance.description,
            'location': instance.location,
            'start_time': instance.start_time.isoformat(),
            'end_time': instance.end_time.isoformat(),
            'status': instance.status,
            'quota': instance.quota,
            'category': instance.category,
            'organizer': self.get_organizer(instance),
            'created_at': instance.created_at.isoformat(),
            'updated_at': instance.updated_at.isoformat(),
        }


class EventUpdateSerializer(serializers.ModelSerializer):
    organizer_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = Event
        fields = [
            'name', 'description', 'location', 'start_time', 'end_time', 
            'status', 'quota', 'category', 'organizer_id'
        ]
    
    def validate_organizer_id(self, value):
        try:
            User.objects.get(id=value)
            return value
        except User.DoesNotExist:
            raise serializers.ValidationError("Organizer not found.")
    
    def update(self, instance, validated_data):
        organizer_id = validated_data.pop('organizer_id', None)
        if organizer_id:
            organizer = User.objects.get(id=organizer_id)
            instance.organizer = organizer
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance