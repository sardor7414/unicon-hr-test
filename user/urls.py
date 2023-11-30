from django.urls import path
from .views import UserLoginAPI, UserRegisterAPI


urlpatterns = [
    path('login/', UserLoginAPI.as_view()),
    path('register/', UserRegisterAPI.as_view())
]
