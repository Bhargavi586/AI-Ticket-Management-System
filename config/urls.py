
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    # Version 1 APIs
    path('api/v1/accounts/', include('accounts.urls')),
]
