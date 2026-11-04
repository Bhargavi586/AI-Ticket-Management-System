from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import User
from .serializers import RegisterSerializer, GoogleLoginSerializer
from .permissions import IsAdmin, IsCustomer, IsSupportAgent, IsTeamLead


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user.role
        token['username'] = user.username
        token['email'] = user.email
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data.update({
            'username': self.user.username,
            'email': self.user.email,
            'role': self.user.role,
        })
        return data


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            "message": "Registration successful!",
            "username": user.username,
            "email": user.email,
            "role": user.role,
        }, status=status.HTTP_201_CREATED)


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "message": "Authentication successful!",
            "username": request.user.username,
            "email": request.user.email,
            "role": request.user.role,
        })


class CustomerDashboardView(APIView):
    permission_classes = [IsCustomer]

    def get(self, request):
        return Response({
            "message": "Welcome to Customer Dashboard!",
            "username": request.user.username,
            "role": request.user.role,
        })


class AdminDashboardView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        return Response({
            "message": "Welcome to Admin Dashboard!",
            "username": request.user.username,
            "role": request.user.role,
        })


class SupportAgentDashboardView(APIView):
    permission_classes = [IsSupportAgent]

    def get(self, request):
        return Response({
            "message": "Welcome to Support Agent Dashboard!",
            "username": request.user.username,
            "role": request.user.role,
        })


class TeamLeadDashboardView(APIView):
    permission_classes = [IsTeamLead]

    def get(self, request):
        return Response({
            "message": "Welcome to Team Lead Dashboard!",
            "username": request.user.username,
            "role": request.user.role,
        })


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response(
                {"error": "Refresh token is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            RefreshToken(refresh_token).blacklist()
        except Exception:
            return Response(
                {"error": "Invalid or expired refresh token."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            {"message": "Logout successful!"},
            status=status.HTTP_200_OK,
        )


def issue_tokens(user):
    refresh = RefreshToken.for_user(user)
    refresh['role'] = user.role
    refresh['username'] = user.username
    refresh['email'] = user.email
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class GoogleLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = GoogleLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        google_data = serializer.validated_data['token']
        email = google_data['email'].strip().lower()
        google_sub = google_data['sub']

        try:
            with transaction.atomic():
                user = User.objects.select_for_update().filter(
                    google_sub=google_sub
                ).first()

                if user is None:
                    # Never silently attach a Google identity to an existing
                    # password account based on email alone.
                    existing_email_user = User.objects.filter(
                        email__iexact=email
                    ).first()
                    if existing_email_user:
                        return Response({
                            "error": (
                                "An account with this email already exists. "
                                "Sign in with your password, then link Google "
                                "using the authenticated google-link endpoint."
                            )
                        }, status=status.HTTP_409_CONFLICT)

                    base_username = f"google_{google_sub}"[:140]
                    username = base_username
                    suffix = 1
                    while User.objects.filter(username=username).exists():
                        username = f"{base_username[:135]}_{suffix}"
                        suffix += 1

                    user = User(
                        username=username,
                        email=email,
                        role=User.Role.CUSTOMER,
                        google_sub=google_sub,
                    )
                    user.set_unusable_password()
                    user.save()
                    created = True
                else:
                    created = False
                    if user.email.lower() != email:
                        return Response(
                            {"error": "Google account email does not match the linked account."},
                            status=status.HTTP_403_FORBIDDEN,
                        )

                if not user.is_active:
                    return Response(
                        {"error": "This account is inactive."},
                        status=status.HTTP_403_FORBIDDEN,
                    )
        except IntegrityError:
            # A concurrent first login may have created this Google identity.
            user = User.objects.filter(google_sub=google_sub).first()
            if user is None:
                return Response(
                    {"error": "Unable to create the account. Please try again."},
                    status=status.HTTP_409_CONFLICT,
                )
            created = False

        response_data = {
            "message": "Google login successful!",
            "created": created,
            "username": user.username,
            "email": user.email,
            "role": user.role,
        }
        response_data.update(issue_tokens(user))
        return Response(response_data, status=status.HTTP_200_OK)


class GoogleAccountLinkView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = GoogleLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        google_data = serializer.validated_data['token']
        google_email = google_data['email'].strip().lower()
        google_sub = google_data['sub']

        if request.user.email.lower() != google_email:
            return Response(
                {"error": "The Google email must match your signed-in account email."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        linked_user = User.objects.filter(google_sub=google_sub).exclude(
            pk=request.user.pk
        ).first()
        if linked_user:
            return Response(
                {"error": "This Google account is already linked to another user."},
                status=status.HTTP_409_CONFLICT,
            )

        request.user.google_sub = google_sub
        try:
            request.user.save(update_fields=['google_sub'])
        except IntegrityError:
            return Response(
                {"error": "This Google account is already linked to another user."},
                status=status.HTTP_409_CONFLICT,
            )

        return Response(
            {"message": "Google account linked successfully."},
            status=status.HTTP_200_OK,
        )
