from django.contrib import admin
from .models import AgentProfile


@admin.register(AgentProfile)
class AgentProfileAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'user',
        'employee_id',
        'phone_number',
        'department',
        'availability',
        'created_at',
    )

    search_fields = (
        'user__username',
        'user__email',
        'employee_id',
        'phone_number',
    )

    list_filter = (
        'availability',
        'department',
        'created_at',
    )