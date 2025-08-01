from django.urls import path
from .views import RegistrationsView, RegistrationDetailView

urlpatterns = [
    path('', RegistrationsView.as_view(), name='registrations'),
    path('<uuid:registration_id>/', RegistrationDetailView.as_view(), name='registration_detail'),
]