from django.urls import path
from .views import groups_list_create, group_detail

urlpatterns = [
    path('', groups_list_create, name='groups_list_create'),
    path('<int:group_id>/', group_detail, name='group_detail'),
]