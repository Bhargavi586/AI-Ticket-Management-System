from django.db import models
from django.conf import settings


class AgentProfile(models.Model):

    class Availability(models.TextChoices):
        AVAILABLE = 'AVAILABLE', 'Available'
        BUSY = 'BUSY', 'Busy'
        OFFLINE = 'OFFLINE', 'Offline'

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='agent_profile'
    )

    employee_id = models.CharField(
        max_length=30,
        unique=True
    )

    phone_number = models.CharField(
        max_length=15,
        blank=True,
        null=True
    )

    department = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    availability = models.CharField(
        max_length=20,
        choices=Availability.choices,
        default=Availability.AVAILABLE
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.employee_id}"