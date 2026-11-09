from rest_framework import serializers
from .models import CustomerProfile


class CustomerProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        source='user.username',
        read_only=True
    )

    email = serializers.EmailField(
        source='user.email',
        read_only=True
    )

    class Meta:
        model = CustomerProfile
        fields = [
            'id',
            'username',
            'email',
            'phone_number',
            'address',
            'profile_picture',
            'created_at',
            'updated_at',
        ]

        read_only_fields = [
            'id',
            'username',
            'email',
            'created_at',
            'updated_at',
        ]