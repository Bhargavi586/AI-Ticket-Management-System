
from rest_framework import serializers
from .models import AgentProfile


class AgentProfileSerializer(serializers.ModelSerializer):

    username = serializers.CharField(
        source='user.username',
        read_only=True
    )

    email = serializers.EmailField(
        source='user.email',
        read_only=True
    )

    class Meta:
        model = AgentProfile

        fields = [
            'id',
            'username',
            'email',
            'employee_id',
            'phone_number',
            'department',
            'availability',
            'created_at',
            'updated_at',
        ]

        read_only_fields = [
            'id',
            'username',
            'email',
            'employee_id',
            'created_at',
            'updated_at',
        ]
