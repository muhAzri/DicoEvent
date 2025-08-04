from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.cache import cache
from django.conf import settings
from loguru import logger
from users.permissions import IsAdminOrSuperUser, IsAuthenticatedUser
from .models import Registration
from .serializers import (
    RegistrationCreateSerializer,
    RegistrationListSerializer,
    RegistrationDetailSerializer,
    RegistrationUpdateSerializer,
)


class RegistrationsView(APIView):
    def get_permissions(self):
        if self.request.method == "GET":
            return [IsAdminOrSuperUser()]
        return [IsAuthenticatedUser()]

    def get(self, request):
        # Try to get from cache first
        cache_key = "registrations_list"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            # Return cached data with X-Data-Source header
            response = Response(cached_data, status=status.HTTP_200_OK)
            response['X-Data-Source'] = 'cache'
            return response
        
        # If not in cache, get from database
        registrations = Registration.objects.all()
        serializer = RegistrationListSerializer(registrations, many=True)
        data = {"registrations": serializer.data}
        
        # Cache the data for 1 hour
        cache.set(cache_key, data, settings.CACHE_TTL)
        
        # Return fresh data with X-Data-Source header
        response = Response(data, status=status.HTTP_200_OK)
        response['X-Data-Source'] = 'database'
        return response

    def post(self, request):
        logger.info(f"POST /registrations - User: {getattr(request.user, 'username', 'anonymous')} - Creating new registration")
        
        try:
            serializer = RegistrationCreateSerializer(data=request.data)
            if serializer.is_valid():
                registration = serializer.save()
                
                # Invalidate registrations list cache
                cache.delete("registrations_list")
                
                logger.info(f"Registration {registration.id} created successfully by {getattr(request.user, 'username', 'anonymous')}")
                return Response(
                    serializer.to_representation(registration),
                    status=status.HTTP_201_CREATED,
                )
            else:
                logger.warning(f"Registration creation failed - Validation errors: {serializer.errors}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f"Error creating registration: {str(e)}")
            return Response(
                {"error": "Failed to create registration"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class RegistrationDetailView(APIView):
    def get_permissions(self):
        if self.request.method == "GET":
            return [IsAuthenticatedUser()]
        return [IsAdminOrSuperUser()]

    def get_object(self, registration_id):
        try:
            return Registration.objects.get(id=registration_id)
        except Registration.DoesNotExist:
            return None

    def get(self, request, registration_id):
        # Try to get from cache first
        cache_key = f"registration_detail_{registration_id}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            # Return cached data with X-Data-Source header
            response = Response(cached_data, status=status.HTTP_200_OK)
            response['X-Data-Source'] = 'cache'
            return response
        
        # If not in cache, get from database
        registration = self.get_object(registration_id)
        if registration is None:
            return Response(
                {"detail": "Registration not found."}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = RegistrationDetailSerializer(registration)
        data = serializer.data
        
        # Cache the data for 1 hour
        cache.set(cache_key, data, settings.CACHE_TTL)
        
        # Return fresh data with X-Data-Source header
        response = Response(data, status=status.HTTP_200_OK)
        response['X-Data-Source'] = 'database'
        return response

    def put(self, request, registration_id):
        registration = self.get_object(registration_id)
        if registration is None:
            return Response(
                {"detail": "Registration not found."}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = RegistrationUpdateSerializer(registration, data=request.data)
        if serializer.is_valid():
            updated_registration = serializer.save()
            
            # Invalidate cache for this specific registration detail
            cache.delete(f"registration_detail_{registration_id}")
            # Invalidate registrations list cache
            cache.delete("registrations_list")
            
            response_serializer = RegistrationDetailSerializer(updated_registration)
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, registration_id):
        registration = self.get_object(registration_id)
        if registration is None:
            return Response(
                {"detail": "Registration not found."}, status=status.HTTP_404_NOT_FOUND
            )

        registration.delete()
        
        # Invalidate cache for this specific registration detail
        cache.delete(f"registration_detail_{registration_id}")
        # Invalidate registrations list cache
        cache.delete("registrations_list")
        
        return Response(status=status.HTTP_204_NO_CONTENT)
