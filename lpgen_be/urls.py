from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('oloye/', admin.site.urls),
    path('api/', include('core.urls'))
]
