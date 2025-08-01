from django.urls import path
from users.views import refresh_token

urlpatterns = [
    path('', refresh_token, name='token_refresh'),
]