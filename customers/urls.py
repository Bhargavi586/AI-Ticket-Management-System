from django.urls import path
from .views import (
    CustomerProfileView,
    CustomerListView,
    CustomerDetailView,
)

urlpatterns = [
    # Customer's own profile
    path('profile/', CustomerProfileView.as_view(), name='customer-profile'),

    # Staff customer information APIs
    path('', CustomerListView.as_view(), name='customer-list'),
    path('<int:pk>/', CustomerDetailView.as_view(), name='customer-detail'),
]