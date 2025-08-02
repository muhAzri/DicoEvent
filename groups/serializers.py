from rest_framework import serializers
from django.contrib.auth.models import Group


class GroupCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ["name"]

    def to_representation(self, instance):
        return {
            "id": instance.id,
            "name": instance.name,
        }


class GroupListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ["id", "name"]

    def to_representation(self, instance):
        return {
            "id": instance.id,
            "name": instance.name,
        }


class GroupDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ["id", "name"]

    def to_representation(self, instance):
        return {
            "id": instance.id,
            "name": instance.name,
        }


class GroupUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ["name"]

    def to_representation(self, instance):
        return {
            "id": instance.id,
            "name": instance.name,
        }
