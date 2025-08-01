from django.urls import path
from .views import UsersView, login

urlpatterns = [
    path('', UsersView.as_view(), name='users'),
    path('login/', login, name='login'),
]