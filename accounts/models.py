from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    class Role(models.TextChoices):
        CUSTOMER = 'CUSTOMER', 'Customer'
        SUPPORT_AGENT = 'SUPPORT_AGENT', 'Support Agent'
        TEAM_LEAD = 'TEAM_LEAD', 'Team Lead'
        ADMIN = 'ADMIN', 'Admin'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CUSTOMER,
    )
    email = models.EmailField(unique=True)
    google_sub = models.CharField(
        max_length=255,
        unique=True,
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"{self.username} - {self.role}"
