from django.urls import path
from .views import EventsView, EventDetailView, EventPosterUploadView, EventPosterView, SendEventRemindersView

urlpatterns = [
    path("", EventsView.as_view(), name="events"),
    path("<uuid:event_id>/", EventDetailView.as_view(), name="event_detail"),
    path("upload/", EventPosterUploadView.as_view(), name="event_poster_upload"),
    path("<uuid:event_id>/poster/", EventPosterView.as_view(), name="event_poster"),
    path("send-reminders/", SendEventRemindersView.as_view(), name="send_event_reminders"),
]
