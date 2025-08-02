from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from users.permissions import IsAdminOrSuperUser, IsAuthenticatedUser
from .models import Registration
from .serializers import RegistrationCreateSerializer, RegistrationListSerializer, RegistrationDetailSerializer, RegistrationUpdateSerializer


class RegistrationsView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAdminOrSuperUser()]
        return [IsAuthenticatedUser()]
    
    def get(self, request):
        registrations = Registration.objects.all()
        serializer = RegistrationListSerializer(registrations, many=True)
        return Response({
            'registrations': serializer.data
        }, status=status.HTTP_200_OK)
    
    def post(self, request):
        serializer = RegistrationCreateSerializer(data=request.data)
        if serializer.is_valid():
            registration = serializer.save()
            return Response(serializer.to_representation(registration), status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegistrationDetailView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticatedUser()]
        return [IsAdminOrSuperUser()]
    
    def get_object(self, registration_id):
        try:
            return Registration.objects.get(id=registration_id)
        except Registration.DoesNotExist:
            return None
    
    def get(self, request, registration_id):
        registration = self.get_object(registration_id)
        if registration is None:
            return Response({'detail': 'Registration not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = RegistrationDetailSerializer(registration)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request, registration_id):
        registration = self.get_object(registration_id)
        if registration is None:
            return Response({'detail': 'Registration not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = RegistrationUpdateSerializer(registration, data=request.data)
        if serializer.is_valid():
            updated_registration = serializer.save()
            response_serializer = RegistrationDetailSerializer(updated_registration)
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, registration_id):
        registration = self.get_object(registration_id)
        if registration is None:
            return Response({'detail': 'Registration not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        registration.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
