from rest_framework import serializers
from .models import User

from google.auth.transport import requests
from google.oauth2 import id_token
from django.conf import settings


class RegisterSerializer(serializers.ModelSerializer):

    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'password',
            'confirm_password',
        ]

        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError(
                "Passwords do not match."
            )

        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')

        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            role=User.Role.CUSTOMER
        )

        return user


class GoogleLoginSerializer(serializers.Serializer):

    token = serializers.CharField()

    def validate_token(self, value):

        try:
            google_user = id_token.verify_oauth2_token(
                value,
                requests.Request(),
                settings.GOOGLE_CLIENT_ID
            )

            if google_user.get('email_verified') is not True:
                raise serializers.ValidationError(
                    "Google email is not verified."
                )

            return google_user

        except ValueError:
            raise serializers.ValidationError(
                "Invalid Google token."
            )