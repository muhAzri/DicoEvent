from django.urls import path
from .views import TicketsView, TicketDetailView

urlpatterns = [
    path('', TicketsView.as_view(), name='tickets'),
    path('<uuid:ticket_id>/', TicketDetailView.as_view(), name='ticket_detail'),
]