from rest_framework import serializers
from registrations.models import Registration
from .models import Payment


class PaymentCreateSerializer(serializers.ModelSerializer):
    registration_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = Payment
        fields = ['registration_id', 'payment_method', 'payment_status', 'amount_paid']
    
    def validate_registration_id(self, value):
        try:
            Registration.objects.get(id=value)
            return value
        except Registration.DoesNotExist:
            raise serializers.ValidationError("Registration not found.")
    
    def create(self, validated_data):
        registration_id = validated_data.pop('registration_id')
        registration = Registration.objects.get(id=registration_id)
        
        payment = Payment.objects.create(registration=registration, **validated_data)
        return payment
    
    def to_representation(self, instance):
        return {
            'id': str(instance.id),
            'registration': str(instance.registration.id),
            'payment_method': instance.payment_method,
            'payment_status': instance.payment_status,
            'amount_paid': str(instance.amount_paid),
        }


class PaymentListSerializer(serializers.ModelSerializer):
    registration = serializers.SerializerMethodField()
    
    class Meta:
        model = Payment
        fields = [
            'id', 'registration', 'payment_method', 'payment_status', 
            'amount_paid', 'created_at', 'updated_at'
        ]
    
    def get_registration(self, obj):
        return {
            'id': str(obj.registration.id),
            'user': obj.registration.user.username,
            'ticket': obj.registration.ticket.name
        }
    
    def to_representation(self, instance):
        return {
            'id': str(instance.id),
            'registration': self.get_registration(instance),
            'payment_method': instance.payment_method,
            'payment_status': instance.payment_status,
            'amount_paid': str(instance.amount_paid),
            'created_at': instance.created_at.isoformat(),
            'updated_at': instance.updated_at.isoformat(),
        }


class PaymentDetailSerializer(serializers.ModelSerializer):
    registration = serializers.SerializerMethodField()
    
    class Meta:
        model = Payment
        fields = [
            'id', 'registration', 'payment_method', 'payment_status', 
            'amount_paid', 'created_at', 'updated_at'
        ]
    
    def get_registration(self, obj):
        return str(obj.registration.id)
    
    def to_representation(self, instance):
        return {
            'id': str(instance.id),
            'registration': self.get_registration(instance),
            'payment_method': instance.payment_method,
            'payment_status': instance.get_payment_status_display(),
            'amount_paid': str(instance.amount_paid),
            'created_at': instance.created_at.isoformat(),
            'updated_at': instance.updated_at.isoformat(),
        }


class PaymentUpdateSerializer(serializers.ModelSerializer):
    registration_id = serializers.UUIDField(write_only=True, required=False)
    
    class Meta:
        model = Payment
        fields = ['registration_id', 'payment_method', 'payment_status', 'amount_paid']
    
    def validate_registration_id(self, value):
        try:
            Registration.objects.get(id=value)
            return value
        except Registration.DoesNotExist:
            raise serializers.ValidationError("Registration not found.")
    
    def update(self, instance, validated_data):
        registration_id = validated_data.pop('registration_id', None)
        
        if registration_id:
            registration = Registration.objects.get(id=registration_id)
            instance.registration = registration
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance
    
    def to_representation(self, instance):
        return {
            'id': str(instance.id),
            'registration': str(instance.registration.id),
            'payment_method': instance.payment_method,
            'payment_status': instance.get_payment_status_display(),
            'amount_paid': str(instance.amount_paid),
        }