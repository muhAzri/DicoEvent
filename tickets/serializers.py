from rest_framework import serializers
from events.models import Event
from .models import Ticket


class TicketCreateSerializer(serializers.ModelSerializer):
    event_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = Ticket
        fields = [
            'event_id', 'name', 'price', 'sales_start', 'sales_end', 'quota'
        ]
    
    def validate_event_id(self, value):
        try:
            Event.objects.get(id=value)
            return value
        except Event.DoesNotExist:
            raise serializers.ValidationError("Event not found.")
    
    def create(self, validated_data):
        event_id = validated_data.pop('event_id')
        event = Event.objects.get(id=event_id)
        ticket = Ticket.objects.create(event=event, **validated_data)
        return ticket
    
    def to_representation(self, instance):
        return {
            'id': str(instance.id),
            'name': instance.name,
            'price': float(instance.price),
            'sales_start': instance.sales_start.isoformat(),
            'sales_end': instance.sales_end.isoformat(),
            'quota': instance.quota,
        }


class TicketListSerializer(serializers.ModelSerializer):
    event = serializers.SerializerMethodField()
    
    class Meta:
        model = Ticket
        fields = [
            'id', 'name', 'price', 'sales_start', 'sales_end', 'quota', 
            'event', 'created_at', 'updated_at'
        ]
    
    def get_event(self, obj):
        return {
            'id': str(obj.event.id),
            'name': obj.event.name
        }
    
    def to_representation(self, instance):
        return {
            'id': str(instance.id),
            'name': instance.name,
            'price': float(instance.price),
            'sales_start': instance.sales_start.isoformat(),
            'sales_end': instance.sales_end.isoformat(),
            'quota': instance.quota,
            'event': self.get_event(instance),
            'created_at': instance.created_at.isoformat(),
            'updated_at': instance.updated_at.isoformat(),
        }


class TicketDetailSerializer(serializers.ModelSerializer):
    event = serializers.SerializerMethodField()
    
    class Meta:
        model = Ticket
        fields = [
            'id', 'event', 'name', 'price', 'sales_start', 'sales_end', 'quota',
            'created_at', 'updated_at'
        ]
    
    def get_event(self, obj):
        return obj.event.name
    
    def to_representation(self, instance):
        return {
            'id': str(instance.id),
            'event': self.get_event(instance),
            'name': instance.name,
            'price': float(instance.price),
            'sales_start': instance.sales_start.isoformat(),
            'sales_end': instance.sales_end.isoformat(),
            'quota': instance.quota,
            'created_at': instance.created_at.isoformat(),
            'updated_at': instance.updated_at.isoformat(),
        }


class TicketUpdateSerializer(serializers.ModelSerializer):
    event_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = Ticket
        fields = [
            'event_id', 'name', 'price', 'sales_start', 'sales_end', 'quota'
        ]
    
    def validate_event_id(self, value):
        try:
            Event.objects.get(id=value)
            return value
        except Event.DoesNotExist:
            raise serializers.ValidationError("Event not found.")
    
    def update(self, instance, validated_data):
        event_id = validated_data.pop('event_id', None)
        if event_id:
            event = Event.objects.get(id=event_id)
            instance.event = event
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance