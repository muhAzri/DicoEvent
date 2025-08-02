from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
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
        tickets = Ticket.objects.all()
        serializer = TicketListSerializer(tickets, many=True)
        return Response({"tickets": serializer.data}, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = TicketCreateSerializer(data=request.data)
        if serializer.is_valid():
            ticket = serializer.save()
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
        ticket = self.get_object(ticket_id)
        if ticket is None:
            return Response(
                {"detail": "Ticket not found."}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = TicketDetailSerializer(ticket)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, ticket_id):
        ticket = self.get_object(ticket_id)
        if ticket is None:
            return Response(
                {"detail": "Ticket not found."}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = TicketUpdateSerializer(ticket, data=request.data)
        if serializer.is_valid():
            updated_ticket = serializer.save()
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
        return Response(status=status.HTTP_204_NO_CONTENT)
