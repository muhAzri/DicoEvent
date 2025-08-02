from django.urls import path
from .views import PaymentsView, PaymentDetailView

urlpatterns = [
    path('', PaymentsView.as_view(), name='payments'),
    path('<uuid:payment_id>/', PaymentDetailView.as_view(), name='payment_detail'),
]