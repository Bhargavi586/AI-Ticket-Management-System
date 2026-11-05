
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    RegisterView,
    CustomTokenObtainPairView,
    ProfileView,
    CustomerDashboardView,
    AdminDashboardView,
    SupportAgentDashboardView,
    TeamLeadDashboardView,
    LogoutView,
    GoogleLoginView,
    GoogleAccountLinkView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('profile/', ProfileView.as_view(), name='profile'),

    path('customer-dashboard/', CustomerDashboardView.as_view(), name='customer_dashboard'),
    path('admin-dashboard/', AdminDashboardView.as_view(), name='admin_dashboard'),
    path('support-dashboard/', SupportAgentDashboardView.as_view(), name='support_dashboard'),
    path('teamlead-dashboard/', TeamLeadDashboardView.as_view(), name='teamlead_dashboard'),

    path('logout/', LogoutView.as_view(), name='logout'),

    path('google-login/', GoogleLoginView.as_view(), name='google-login'),
    path('google-link/', GoogleAccountLinkView.as_view(), name='google-link'),

    # Password Reset APIs
    path('password-reset/', PasswordResetRequestView.as_view(), name='password_reset'),
    path('password-reset/confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
]
