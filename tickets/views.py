from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.core.cache import cache
from django.conf import settings
from users.permissions import IsAdminOrSuperUser
from .models import Ticket
from .serializers import (
    TicketCreateSerializer,
    TicketListSerializer,
    TicketDetailSerializer,
    TicketUpdateSerializer,
)


class TicketsView(APIView):
    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAdminOrSuperUser()]

    def get(self, request):
        # Try to get from cache first
        cache_key = "tickets_list"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            # Return cached data with X-Data-Source header
            response = Response(cached_data, status=status.HTTP_200_OK)
            response['X-Data-Source'] = 'cache'
            return response
        
        # If not in cache, get from database
        tickets = Ticket.objects.all()
        serializer = TicketListSerializer(tickets, many=True)
        data = {"tickets": serializer.data}
        
        # Cache the data for 1 hour
        cache.set(cache_key, data, settings.CACHE_TTL)
        
        # Return fresh data with X-Data-Source header
        response = Response(data, status=status.HTTP_200_OK)
        response['X-Data-Source'] = 'database'
        return response

    def post(self, request):
        serializer = TicketCreateSerializer(data=request.data)
        if serializer.is_valid():
            ticket = serializer.save()
            
            # Invalidate tickets list cache
            cache.delete("tickets_list")
            
            return Response(
                serializer.to_representation(ticket), status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TicketDetailView(APIView):
    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAdminOrSuperUser()]

    def get_object(self, ticket_id):
        try:
            return Ticket.objects.get(id=ticket_id)
        except Ticket.DoesNotExist:
            return None

    def get(self, request, ticket_id):
        # Try to get from cache first
        cache_key = f"ticket_detail_{ticket_id}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            # Return cached data with X-Data-Source header
            response = Response(cached_data, status=status.HTTP_200_OK)
            response['X-Data-Source'] = 'cache'
            return response
        
        # If not in cache, get from database
        ticket = self.get_object(ticket_id)
        if ticket is None:
            return Response(
                {"detail": "Ticket not found."}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = TicketDetailSerializer(ticket)
        data = serializer.data
        
        # Cache the data for 1 hour
        cache.set(cache_key, data, settings.CACHE_TTL)
        
        # Return fresh data with X-Data-Source header
        response = Response(data, status=status.HTTP_200_OK)
        response['X-Data-Source'] = 'database'
        return response

    def put(self, request, ticket_id):
        ticket = self.get_object(ticket_id)
        if ticket is None:
            return Response(
                {"detail": "Ticket not found."}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = TicketUpdateSerializer(ticket, data=request.data)
        if serializer.is_valid():
            updated_ticket = serializer.save()
            
            # Invalidate cache for this specific ticket detail
            cache.delete(f"ticket_detail_{ticket_id}")
            # Invalidate tickets list cache
            cache.delete("tickets_list")
            
            response_serializer = TicketDetailSerializer(updated_ticket)
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, ticket_id):
        ticket = self.get_object(ticket_id)
        if ticket is None:
            return Response(
                {"detail": "Ticket not found."}, status=status.HTTP_404_NOT_FOUND
            )

        ticket.delete()
        
        # Invalidate cache for this specific ticket detail
        cache.delete(f"ticket_detail_{ticket_id}")
        # Invalidate tickets list cache
        cache.delete("tickets_list")
        
        return Response(status=status.HTTP_204_NO_CONTENT)
