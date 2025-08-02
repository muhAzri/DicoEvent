from django.urls import path
from .views import EventsView, EventDetailView

urlpatterns = [
    path("", EventsView.as_view(), name="events"),
    path("<uuid:event_id>/", EventDetailView.as_view(), name="event_detail"),
]
