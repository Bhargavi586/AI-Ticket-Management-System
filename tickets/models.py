
from django.db import models, transaction
from django.conf import settings
from django.utils import timezone
from categories.models import Category


class Ticket(models.Model):

    class Priority(models.TextChoices):
        LOW = 'LOW', 'Low'
        MEDIUM = 'MEDIUM', 'Medium'
        HIGH = 'HIGH', 'High'
        URGENT = 'URGENT', 'Urgent'

    class Status(models.TextChoices):
        OPEN = 'OPEN', 'Open'
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
        WAITING = 'WAITING', 'Waiting'
        RESOLVED = 'RESOLVED', 'Resolved'
        CLOSED = 'CLOSED', 'Closed'

    ticket_id = models.CharField(
        max_length=30,
        unique=True,
        editable=False,
        blank=True
    )

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='customer_tickets'
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='tickets'
    )

    subject = models.CharField(max_length=200)
    description = models.TextField()

    priority = models.CharField(
        max_length=10,
        choices=Priority.choices,
        default=Priority.MEDIUM
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.OPEN
    )

    assigned_agent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tickets'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):

        if not self.ticket_id:
            with transaction.atomic():
                year = timezone.now().year

                last_ticket = Ticket.objects.filter(
                    category=self.category,
                    created_at__year=year
                ).order_by('-id').first()

                next_number = 1

                if last_ticket and last_ticket.ticket_id:
                    next_number = int(
                        last_ticket.ticket_id.split('-')[-1]
                    ) + 1

                self.ticket_id = (
                    f"{self.category.code}-{year}-{next_number:05d}"
                )

                super().save(*args, **kwargs)
                return

        super().save(*args, **kwargs)

    def __str__(self):
        return self.ticket_id

class TicketHistory(models.Model):

    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name='history'
    )

    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    action = models.CharField(max_length=100)

    old_value = models.TextField(blank=True, null=True)

    new_value = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.ticket.ticket_id} - {self.action}"
