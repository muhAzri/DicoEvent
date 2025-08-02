from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from users.permissions import IsAdminOrSuperUser
from .models import Event
from .serializers import EventCreateSerializer, EventListSerializer, EventUpdateSerializer


class EventsView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAdminOrSuperUser()]
    
    def get(self, request):
        events = Event.objects.all().order_by('-created_at')
        
        # Get page number from query params
        page_number = request.GET.get('page', 1)
        page_size = 10  # Events per page
        
        # Create paginator
        paginator = Paginator(events, page_size)
        
        try:
            page_obj = paginator.page(page_number)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)
        
        # Serialize paginated data
        serializer = EventListSerializer(page_obj, many=True)
        
        return Response({
            'events': serializer.data,
            'pagination': {
                'page': page_obj.number,
                'pages': paginator.num_pages,
                'per_page': page_size,
                'total': paginator.count,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous(),
                'next_page': page_obj.next_page_number() if page_obj.has_next() else None,
                'previous_page': page_obj.previous_page_number() if page_obj.has_previous() else None
            }
        }, status=status.HTTP_200_OK)
    
    def post(self, request):
        serializer = EventCreateSerializer(data=request.data)
        if serializer.is_valid():
            event = serializer.save()
            return Response(serializer.to_representation(event), status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EventDetailView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAdminOrSuperUser()]
    
    def get_object(self, event_id):
        try:
            return Event.objects.get(id=event_id)
        except Event.DoesNotExist:
            return None
    
    def get(self, request, event_id):
        event = self.get_object(event_id)
        if event is None:
            return Response({'detail': 'Event not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = EventListSerializer(event)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request, event_id):
        event = self.get_object(event_id)
        if event is None:
            return Response({'detail': 'Event not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = EventUpdateSerializer(event, data=request.data)
        if serializer.is_valid():
            updated_event = serializer.save()
            response_serializer = EventListSerializer(updated_event)
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, event_id):
        event = self.get_object(event_id)
        if event is None:
            return Response({'detail': 'Event not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        event.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
