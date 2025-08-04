from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.cache import cache
from django.conf import settings
from users.permissions import (
    IsAdminOrSuperUser,
    IsOrganizerAdminOrSuperUser,
    IsOrganizerOwnerOrAdmin,
)
from .models import Event
from .serializers import (
    EventCreateSerializer,
    EventListSerializer,
    EventUpdateSerializer,
    EventPosterUploadSerializer,
)
from .tasks import send_event_reminders


class EventsView(APIView):
    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsOrganizerAdminOrSuperUser()]

    def get(self, request):
        # Get page number from query params
        page_number = request.GET.get("page", 1)
        page_size = 10  # Events per page
        
        # Try to get from cache first
        cache_key = f"events_list_page_{page_number}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            # Return cached data with X-Data-Source header
            response = Response(cached_data, status=status.HTTP_200_OK)
            response['X-Data-Source'] = 'cache'
            return response
        
        # If not in cache, get from database
        events = Event.objects.all().order_by("-created_at")

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

        data = {
            "events": serializer.data,
            "pagination": {
                "page": page_obj.number,
                "pages": paginator.num_pages,
                "per_page": page_size,
                "total": paginator.count,
                "has_next": page_obj.has_next(),
                "has_previous": page_obj.has_previous(),
                "next_page": (
                    page_obj.next_page_number() if page_obj.has_next() else None
                ),
                "previous_page": (
                    page_obj.previous_page_number()
                    if page_obj.has_previous()
                    else None
                ),
            },
        }
        
        # Cache the data for 1 hour
        cache.set(cache_key, data, settings.CACHE_TTL)
        
        # Return fresh data with X-Data-Source header
        response = Response(data, status=status.HTTP_200_OK)
        response['X-Data-Source'] = 'database'
        return response

    def post(self, request):
        serializer = EventCreateSerializer(data=request.data)
        if serializer.is_valid():
            event = serializer.save()
            
            # Invalidate cache for events list (all pages)
            self._invalidate_events_cache()
            
            return Response(
                serializer.to_representation(event), status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    def _invalidate_events_cache(self):
        """Invalidate all events list cache pages."""
        # Clear all events list cache pages
        for page in range(1, 100):  # Assume max 100 pages
            cache.delete(f"events_list_page_{page}")


class EventDetailView(APIView):
    permission_classes = [IsOrganizerOwnerOrAdmin]

    def get_object(self, event_id):
        try:
            return Event.objects.get(id=event_id)
        except Event.DoesNotExist:
            return None

    def get(self, request, event_id):
        # Try to get from cache first
        cache_key = f"event_detail_{event_id}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            # Return cached data with X-Data-Source header
            response = Response(cached_data, status=status.HTTP_200_OK)
            response['X-Data-Source'] = 'cache'
            return response
        
        # If not in cache, get from database
        event = self.get_object(event_id)
        if event is None:
            return Response(
                {"detail": "Event not found."}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = EventListSerializer(event)
        data = serializer.data
        
        # Cache the data for 1 hour
        cache.set(cache_key, data, settings.CACHE_TTL)
        
        # Return fresh data with X-Data-Source header
        response = Response(data, status=status.HTTP_200_OK)
        response['X-Data-Source'] = 'database'
        return response

    def put(self, request, event_id):
        event = self.get_object(event_id)
        if event is None:
            return Response(
                {"detail": "Event not found."}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = EventUpdateSerializer(event, data=request.data)
        if serializer.is_valid():
            updated_event = serializer.save()
            
            # Invalidate cache for this specific event detail
            cache.delete(f"event_detail_{event_id}")
            
            # Invalidate cache for events list (all pages)
            self._invalidate_events_cache()
            
            response_serializer = EventListSerializer(updated_event)
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, event_id):
        event = self.get_object(event_id)
        if event is None:
            return Response(
                {"detail": "Event not found."}, status=status.HTTP_404_NOT_FOUND
            )

        event.delete()
        
        # Invalidate cache for this specific event detail
        cache.delete(f"event_detail_{event_id}")
        
        # Invalidate cache for events list (all pages)
        self._invalidate_events_cache()
        
        return Response(status=status.HTTP_204_NO_CONTENT)
        
    def _invalidate_events_cache(self):
        """Invalidate all events list cache pages."""
        # Clear all events list cache pages
        for page in range(1, 100):  # Assume max 100 pages
            cache.delete(f"events_list_page_{page}")


class EventPosterUploadView(APIView):
    permission_classes = [IsOrganizerAdminOrSuperUser]
    
    def post(self, request):
        """Upload event poster."""
        serializer = EventPosterUploadSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                result = serializer.save()
                
                # Invalidate cache for the specific event detail
                event_id = result.get('id')
                if event_id:
                    cache.delete(f"event_detail_{event_id}")
                
                # Invalidate cache for events list (all pages)
                self._invalidate_events_cache()
                
                return Response(result, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response(
                    {"error": f"Upload failed: {str(e)}"}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    def _invalidate_events_cache(self):
        """Invalidate all events list cache pages."""
        # Clear all events list cache pages
        for page in range(1, 100):  # Assume max 100 pages
            cache.delete(f"events_list_page_{page}")


class EventPosterView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request, event_id):
        """Get event poster URL."""
        try:
            event = Event.objects.get(id=event_id)
            
            if not event.poster:
                return Response(
                    {"detail": "Event poster not found."}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Generate presigned URL for the poster
            try:
                from .services import minio_service
                poster_url = minio_service.get_file_url(
                    event.poster, 
                    folder="event-posters",
                    expires=3600  # 1 hour
                )
                
                return Response({
                    "event_id": str(event.id),
                    "poster_url": poster_url,
                    "filename": event.poster
                }, status=status.HTTP_200_OK)
                
            except Exception as e:
                return Response(
                    {"error": f"Failed to generate poster URL: {str(e)}"}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
        except Event.DoesNotExist:
            return Response(
                {"detail": "Event not found."}, 
                status=status.HTTP_404_NOT_FOUND
            )


class SendEventRemindersView(APIView):
    permission_classes = [IsAdminOrSuperUser]
    
    def post(self, request):
        """Manually trigger event reminder emails."""
        try:
            # Trigger the Celery task
            task = send_event_reminders.delay()
            
            return Response({
                "message": "Event reminder task has been queued successfully",
                "task_id": task.id
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                "error": f"Failed to queue reminder task: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
