from django.urls import path

from .views import LoginAPI, UpdateIsActiveAPIView
from .views import RegisterAPI

urlpatterns = [
    path('api/register/', RegisterAPI.as_view(), name='register'),
    path('api/login/', LoginAPI.as_view(), name='login'),
    path('api/delete/', UpdateIsActiveAPIView.as_view(), name='soft_delete_user'),
]
