from django.urls import path, include
from .views import (ContentGeneration, LoginUserView, CreateUserView,
                    LogoutUserView, DashboardView, ContentView, IdeaViewSet)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'ideas', IdeaViewSet, basename='idea')


urlpatterns = [
    path('generate-content/', ContentGeneration.as_view(), name="contentgeneration"),
    path('dashboard/', DashboardView.as_view(), name="dashboard"),
    path('loginuser/', LoginUserView.as_view(), name="loginuser"),
    path('registeruser/', CreateUserView.as_view(), name="registeruser"),
    path('logoutuser/', LogoutUserView.as_view(), name="logoutuser"),
    path('idea/<int:idea_id>/', ContentView.as_view(), name='idea-view'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('', include(router.urls)),

]
