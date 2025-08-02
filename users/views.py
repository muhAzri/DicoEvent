from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from .serializers import UserRegistrationSerializer, LoginSerializer, UserListSerializer, UserDetailSerializer, UserUpdateSerializer
from .permissions import IsAdminOrSuperUser, IsOwnerOrReadOnly, UserDetailPermission

User = get_user_model()


class UsersView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAdminOrSuperUser()]
        return [AllowAny()]
    
    def get(self, request):
        users = User.objects.all()
        serializer = UserListSerializer(users, many=True)
        return Response({
            'users': serializer.data
        }, status=status.HTTP_200_OK)
    
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(serializer.to_representation(user), status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDetailView(APIView):
    permission_classes = [UserDetailPermission]
    
    def get_object(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None
    
    def get(self, request, user_id):
        user = self.get_object(user_id)
        if user is None:
            return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = UserDetailSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request, user_id):
        user = self.get_object(user_id)
        if user is None:
            return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        # Check object permission
        self.check_object_permissions(request, user)
        
        serializer = UserUpdateSerializer(user, data=request.data)
        if serializer.is_valid():
            updated_user = serializer.save()
            response_serializer = UserDetailSerializer(updated_user)
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, user_id):
        user = self.get_object(user_id)
        if user is None:
            return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        # Check object permission
        self.check_object_permissions(request, user)
        
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
def login(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        tokens = serializer.save()
        return Response(tokens, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def refresh_token(request):
    refresh_token = request.data.get('refresh')
    
    if not refresh_token:
        return Response({'detail': 'Refresh token is required.'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        refresh = RefreshToken(refresh_token)
        user = User.objects.get(id=refresh['user_id'])
        
        # Generate new access token
        new_access_token = refresh.access_token
        # Add user info to new access token
        new_access_token['is_admin'] = user.is_admin
        new_access_token['is_superuser'] = user.is_superuser
        
        return Response({
            'access': str(new_access_token)
        }, status=status.HTTP_200_OK)
        
    except (InvalidToken, TokenError):
        return Response({'detail': 'Invalid refresh token.'}, status=status.HTTP_400_BAD_REQUEST)
    except User.DoesNotExist:
        return Response({'detail': 'User not found.'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def assign_roles(request):
    # Only superuser can assign roles
    if not (request.user and request.user.is_authenticated and request.user.is_superuser):
        return Response({'detail': 'Only superuser can assign roles.'}, status=status.HTTP_403_FORBIDDEN)
    
    user_id = request.data.get('user_id')
    group_id = request.data.get('group_id')
    
    if not user_id or not group_id:
        return Response({'detail': 'user_id and group_id are required.'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
    
    try:
        # Look for group in Django's auth_group table
        group = Group.objects.get(id=group_id)
    except Group.DoesNotExist:
        return Response({'detail': 'Group not found.'}, status=status.HTTP_404_NOT_FOUND)
    
    # Add user to Django group
    user.groups.add(group)
    
    return Response({
        'detail': f'User {user.username} has been assigned to group {group.name}.',
        'user_id': str(user.id),
        'group_id': str(group.id)
    }, status=status.HTTP_200_OK)
