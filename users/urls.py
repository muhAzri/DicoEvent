from django.urls import path
from .views import UsersView, UserDetailView, login

urlpatterns = [
    path('', UsersView.as_view(), name='users'),
    path('<uuid:user_id>/', UserDetailView.as_view(), name='user_detail'),
    path('login/', login, name='login'),
]