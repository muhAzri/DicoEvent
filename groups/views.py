from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import Group
from django.core.cache import cache
from django.conf import settings
from users.permissions import IsAdminOrSuperUser
from .serializers import (
    GroupCreateSerializer,
    GroupListSerializer,
    GroupDetailSerializer,
    GroupUpdateSerializer,
)


class GroupsView(APIView):
    permission_classes = [IsAdminOrSuperUser]

    def get(self, request):
        # Try to get from cache first
        cache_key = "groups_list"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            # Return cached data with X-Data-Source header
            response = Response(cached_data, status=status.HTTP_200_OK)
            response['X-Data-Source'] = 'cache'
            return response
        
        # If not in cache, get from database
        groups = Group.objects.all().order_by("name")
        serializer = GroupListSerializer(groups, many=True)
        data = {"groups": serializer.data}
        
        # Cache the data for 1 hour
        cache.set(cache_key, data, settings.CACHE_TTL)
        
        # Return fresh data with X-Data-Source header
        response = Response(data, status=status.HTTP_200_OK)
        response['X-Data-Source'] = 'database'
        return response

    def post(self, request):
        serializer = GroupCreateSerializer(data=request.data)
        if serializer.is_valid():
            group = serializer.save()
            
            # Invalidate groups list cache
            cache.delete("groups_list")
            
            return Response(
                serializer.to_representation(group), status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GroupDetailView(APIView):
    permission_classes = [IsAdminOrSuperUser]

    def get_object(self, group_id):
        try:
            return Group.objects.get(id=group_id)
        except Group.DoesNotExist:
            return None

    def get(self, request, group_id):
        # Try to get from cache first
        cache_key = f"group_detail_{group_id}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            # Return cached data with X-Data-Source header
            response = Response(cached_data, status=status.HTTP_200_OK)
            response['X-Data-Source'] = 'cache'
            return response
        
        # If not in cache, get from database
        group = self.get_object(group_id)
        if group is None:
            return Response(
                {"detail": "Group not found."}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = GroupDetailSerializer(group)
        data = serializer.data
        
        # Cache the data for 1 hour
        cache.set(cache_key, data, settings.CACHE_TTL)
        
        # Return fresh data with X-Data-Source header
        response = Response(data, status=status.HTTP_200_OK)
        response['X-Data-Source'] = 'database'
        return response

    def put(self, request, group_id):
        group = self.get_object(group_id)
        if group is None:
            return Response(
                {"detail": "Group not found."}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = GroupUpdateSerializer(group, data=request.data)
        if serializer.is_valid():
            updated_group = serializer.save()
            
            # Invalidate cache for this specific group detail
            cache.delete(f"group_detail_{group_id}")
            # Invalidate groups list cache
            cache.delete("groups_list")
            
            response_serializer = GroupDetailSerializer(updated_group)
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, group_id):
        group = self.get_object(group_id)
        if group is None:
            return Response(
                {"detail": "Group not found."}, status=status.HTTP_404_NOT_FOUND
            )

        group.delete()
        
        # Invalidate cache for this specific group detail
        cache.delete(f"group_detail_{group_id}")
        # Invalidate groups list cache
        cache.delete("groups_list")
        
        return Response(status=status.HTTP_204_NO_CONTENT)
