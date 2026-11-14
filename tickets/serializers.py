
from rest_framework import serializers
from .models import Ticket


class TicketSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ticket

        fields = [
            'id',
            'ticket_id',
            'customer',
            'category',
            'subject',
            'description',
            'priority',
            'status',
            'assigned_agent',
            'created_at',
            'updated_at',
        ]

        read_only_fields = [
            'id',
            'ticket_id',
            'customer',
            'priority',
            'status',
            'assigned_agent',
            'created_at',
            'updated_at',
        ]

    def validate_category(self, category):
        if not category.is_active:
            raise serializers.ValidationError(
                "This category is inactive."
            )
        return category
