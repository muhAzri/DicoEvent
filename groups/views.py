from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import Group
from users.permissions import IsAdminOrSuperUser
from .serializers import GroupCreateSerializer, GroupListSerializer, GroupDetailSerializer, GroupUpdateSerializer


class GroupsView(APIView):
    permission_classes = [IsAdminOrSuperUser]
    
    def get(self, request):
        groups = Group.objects.all().order_by('name')
        serializer = GroupListSerializer(groups, many=True)
        return Response({
            'groups': serializer.data
        }, status=status.HTTP_200_OK)
    
    def post(self, request):
        serializer = GroupCreateSerializer(data=request.data)
        if serializer.is_valid():
            group = serializer.save()
            return Response(serializer.to_representation(group), status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GroupDetailView(APIView):
    permission_classes = [IsAdminOrSuperUser]
    
    def get_object(self, group_id):
        try:
            return Group.objects.get(id=group_id)
        except Group.DoesNotExist:
            return None
    
    def get(self, request, group_id):
        group = self.get_object(group_id)
        if group is None:
            return Response({'detail': 'Group not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = GroupDetailSerializer(group)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request, group_id):
        group = self.get_object(group_id)  
        if group is None:
            return Response({'detail': 'Group not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = GroupUpdateSerializer(group, data=request.data)
        if serializer.is_valid():
            updated_group = serializer.save()
            response_serializer = GroupDetailSerializer(updated_group)
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, group_id):
        group = self.get_object(group_id)
        if group is None:
            return Response({'detail': 'Group not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        group.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
