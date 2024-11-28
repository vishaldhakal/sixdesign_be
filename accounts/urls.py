from django.urls import path
from .views import (
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    LogoutView,
    UserDetailView,
    UserCreateView
)

app_name = 'accounts'

urlpatterns = [
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='auth_logout'),
    path('user/', UserDetailView.as_view(), name='user_me'),
    path('register/', UserCreateView.as_view(), name='register'),
] 