from django.urls import path
from .views import ContentGeneration, LoginUserView, CreateUserView, LogoutUserView, DashboardView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


urlpatterns = [
    path('generate-content/', ContentGeneration.as_view(), name="contentgeneration"),
    path('dashboard/', DashboardView.as_view(), name="dashboard"),
    path('loginuser/', LoginUserView.as_view(), name="loginuser"),
    path('registeruser/', CreateUserView.as_view(), name="registeruser"),
    path('logoutuser/', LogoutUserView.as_view(), name="logoutuser"),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

]
