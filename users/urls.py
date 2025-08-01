from django.urls import path
from .views import UsersView, UserDetailView, login, assign_roles

urlpatterns = [
    path('', UsersView.as_view(), name='users'),
    path('<uuid:user_id>/', UserDetailView.as_view(), name='user_detail'),
    path('login/', login, name='login'),
    path('assign-roles/', assign_roles, name='assign_roles'),
]