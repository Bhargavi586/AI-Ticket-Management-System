from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token

from .models import User


class RegisterSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'confirm_password']
        extra_kwargs = {'password': {'write_only': True}}

    def validate_email(self, value):
        normalized_email = value.strip().lower()
        if User.objects.filter(email__iexact=normalized_email).exists():
            raise serializers.ValidationError(
                "A user with this email address already exists."
            )
        return normalized_email

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({
                'confirm_password': "Passwords do not match."
            })

        candidate = User(
            username=data.get('username', ''),
            email=data.get('email', ''),
        )
        try:
            validate_password(data['password'], user=candidate)
        except DjangoValidationError as exc:
            raise serializers.ValidationError({'password': list(exc.messages)})
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        return User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            role=User.Role.CUSTOMER,
        )


class GoogleLoginSerializer(serializers.Serializer):
    token = serializers.CharField(write_only=True)

    def validate_token(self, value):
        client_id = getattr(settings, 'GOOGLE_CLIENT_ID', None)
        if not client_id:
            raise serializers.ValidationError(
                "Google login is not configured on the server."
            )
        try:
            payload = id_token.verify_oauth2_token(
                value, google_requests.Request(), client_id
            )
        except (ValueError, Exception) as exc:
            # Do not expose token-validation internals to API clients.
            raise serializers.ValidationError("Invalid Google ID token.") from exc

        if not payload.get('sub') or not payload.get('email'):
            raise serializers.ValidationError(
                "Google token is missing required account information."
            )
        if payload.get('email_verified') is not True:
            raise serializers.ValidationError("Google email is not verified.")
        return payload
