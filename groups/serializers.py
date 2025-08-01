from rest_framework import serializers
from .models import Group


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('id', 'name')
        
    def to_representation(self, instance):
        return {
            'id': instance.id,
            'name': instance.name
        }