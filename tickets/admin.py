from django.contrib import admin
from .models import Ticket


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):

    list_display = (
        'ticket_id',
        'customer',
        'category',
        'priority',
        'status',
        'assigned_agent',
        'created_at',
    )

    search_fields = (
        'ticket_id',
        'subject',
    )

    list_filter = (
        'priority',
        'status',
        'category',
    )