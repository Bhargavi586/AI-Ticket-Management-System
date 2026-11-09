from django.contrib import admin
from .models import CustomerProfile


@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'phone_number',
        'created_at',
        'updated_at',
    )

    search_fields = (
        'user__username',
        'user__email',
        'phone_number',
    )

    list_filter = ('created_at',)