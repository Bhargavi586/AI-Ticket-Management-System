
from django.urls import path
from .views import RegisterView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import ProfileView
from .views import CustomerDashboardView
from .views import AdminDashboardView
from .views import SupportAgentDashboardView
from .views import TeamLeadDashboardView
from .views import LogoutView
from .views import GoogleLoginView
urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),

    path('login/', TokenObtainPairView.as_view(), name='login'),

    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('customer-dashboard/', CustomerDashboardView.as_view(), name='customer_dashboard'),
    path('admin-dashboard/', AdminDashboardView.as_view(), name='admin_dashboard'),
    path(
    'support-dashboard/',
    SupportAgentDashboardView.as_view(),
    name='support_dashboard'
),
path(
    'teamlead-dashboard/',
    TeamLeadDashboardView.as_view(),
    name='teamlead_dashboard'
),
path('logout/', LogoutView.as_view(), name='logout'),
path('google-login/', GoogleLoginView.as_view(), name='google-login'),
]
