from django.urls import path
from .views import ContentGeneration


urlpatterns = [
    path('generate-content/', ContentGeneration.as_view(), name="contentgeneration"),
]
