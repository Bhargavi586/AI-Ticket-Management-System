
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .serializers import RegisterSerializer, GoogleLoginSerializer
from .permissions import (
    IsAdmin,
    IsCustomer,
    IsSupportAgent,
    IsTeamLead
)


class RegisterView(generics.CreateAPIView):

    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(
            {
                "message": "Registration successful!",
                "username": user.username,
                "email": user.email,
                "role": user.role
            },
            status=status.HTTP_201_CREATED
        )


class ProfileView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        return Response({
            "message": "Authentication successful!",
            "username": request.user.username,
            "email": request.user.email,
            "role": request.user.role
        })


class CustomerDashboardView(APIView):

    permission_classes = [IsCustomer]

    def get(self, request):

        return Response({
            "message": "Welcome to Customer Dashboard!",
            "username": request.user.username,
            "role": request.user.role
        })


class AdminDashboardView(APIView):

    permission_classes = [IsAdmin]

    def get(self, request):

        return Response({
            "message": "Welcome to Admin Dashboard!",
            "username": request.user.username,
            "role": request.user.role
        })


class SupportAgentDashboardView(APIView):

    permission_classes = [IsSupportAgent]

    def get(self, request):

        return Response({
            "message": "Welcome to Support Agent Dashboard!",
            "username": request.user.username,
            "role": request.user.role
        })


class TeamLeadDashboardView(APIView):

    permission_classes = [IsTeamLead]

    def get(self, request):

        return Response({
            "message": "Welcome to Team Lead Dashboard!",
            "username": request.user.username,
            "role": request.user.role
        })


class LogoutView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        try:
            refresh_token = request.data.get('refresh')

            if not refresh_token:
                return Response(
                    {"error": "Refresh token is required."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(
                {"message": "Logout successful!"},
                status=status.HTTP_200_OK
            )

        except Exception:
            return Response(
                {"error": "Invalid or expired refresh token."},
                status=status.HTTP_400_BAD_REQUEST
            )


class GoogleLoginView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):

        serializer = GoogleLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        google_user = serializer.validated_data['token']

        email = google_user.get('email')
        email_verified = google_user.get('email_verified')

        if not email or email_verified is not True:
            return Response(
                {"error": "Google email is not verified."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = User.objects.filter(email__iexact=email).first()
        created = False

        if user is None:

            base_username = email.split('@')[0]
            username = base_username
            counter = 1

            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1

            user = User.objects.create_user(
                username=username,
                email=email,
                password=None,
                role=User.Role.CUSTOMER
            )

            created = True

        if not user.is_active:
            return Response(
                {"error": "This account is inactive."},
                status=status.HTTP_403_FORBIDDEN
            )

        refresh = RefreshToken.for_user(user)

        return Response({
            "message": "Google login successful!",
            "created": created,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "refresh": str(refresh),
            "access": str(refresh.access_token)
        }, status=status.HTTP_200_OK)
