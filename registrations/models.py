from django.db import models
from django.contrib.auth import get_user_model
from tickets.models import Ticket
import uuid

User = get_user_model()


class Registration(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='registrations')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='registrations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.ticket.name}"
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['ticket', 'user']  # Prevent duplicate registrations
