from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from tickets.models import Ticket
import uuid

User = get_user_model()


class Registration(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ticket = models.ForeignKey(
        Ticket, on_delete=models.CASCADE, related_name="registrations"
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="registrations"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.ticket.name}"

    class Meta:
        ordering = ["-created_at"]
        unique_together = ["ticket", "user"]  # Prevent duplicate registrations


@receiver(post_save, sender=Registration)
def handle_new_registration(sender, instance, created, **kwargs):
    """
    Send reminder email when new registration is created, if event is within 2 hours
    """
    if created:  # Only for new registrations
        from events.tasks import send_reminder_for_new_registration
        # Trigger the task asynchronously
        send_reminder_for_new_registration.delay(str(instance.id))
