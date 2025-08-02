from django.urls import path
from .views import GroupsView, GroupDetailView

urlpatterns = [
    path('', GroupsView.as_view(), name='groups'),
    path('<int:group_id>/', GroupDetailView.as_view(), name='group_detail'),
]