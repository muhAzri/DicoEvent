from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from loguru import logger
from .models import Event
from registrations.models import Registration

@shared_task
def send_event_reminder_email(user_email, user_name, event_name, event_start_time, event_location):
    """
    Send event reminder email to a specific user
    """
    try:
        subject = f'Event Reminder: {event_name}'
        message = f"""
        Hi {user_name},
        
        This is a reminder that you have registered for the following event:
        
        Event: {event_name}
        Date & Time: {event_start_time}
        Location: {event_location}
        
        The event will start in approximately 2 hours. Please make sure to arrive on time.
        
        Best regards,
        DicoEvent Team
        """
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_email],
            fail_silently=False,
        )
        
        logger.info(f"Reminder email sent successfully to {user_email} for event {event_name}")
        return f"Email sent to {user_email}"
        
    except Exception as e:
        logger.error(f"Failed to send reminder email to {user_email}: {str(e)}")
        raise e

@shared_task
def send_event_reminders():
    """
    Check for events starting in 2 hours and send reminder emails to registered users
    """
    try:
        # Calculate the time range for events starting in approximately 2 hours
        now = timezone.now()
        two_hours_from_now = now + timedelta(hours=2)
        # Add some buffer (15 minutes) to catch events
        time_window_start = two_hours_from_now - timedelta(minutes=15)
        time_window_end = two_hours_from_now + timedelta(minutes=15)
        
        # Find events starting in about 2 hours
        upcoming_events = Event.objects.filter(
            start_time__gte=time_window_start,
            start_time__lte=time_window_end,
            status='scheduled'
        )
        
        reminder_count = 0
        
        for event in upcoming_events:
            # Get all registrations for this event
            registrations = Registration.objects.filter(
                ticket__event=event
            ).select_related('user', 'ticket')
            
            for registration in registrations:
                user = registration.user
                
                # Send reminder email
                send_event_reminder_email.delay(
                    user_email=user.email,
                    user_name=f"{user.first_name} {user.last_name}".strip() or user.username,
                    event_name=event.name,
                    event_start_time=event.start_time.strftime('%Y-%m-%d %H:%M:%S UTC'),
                    event_location=event.location
                )
                
                reminder_count += 1
        
        logger.info(f"Scheduled {reminder_count} reminder emails for {len(upcoming_events)} events")
        return f"Scheduled {reminder_count} reminder emails"
        
    except Exception as e:
        logger.error(f"Error in send_event_reminders task: {str(e)}")
        raise e

@shared_task
def send_reminder_for_new_registration(registration_id):
    """
    Send reminder email for new registration if event starts within 2 hours
    """
    try:
        registration = Registration.objects.select_related('user', 'ticket__event').get(id=registration_id)
        event = registration.ticket.event
        user = registration.user
        
        # Calculate if event starts within 2 hours (with 15 minute buffer)
        now = timezone.now()
        time_until_event = event.start_time - now
        
        # If event starts within 2 hours and 15 minutes, send reminder
        if timedelta(hours=1, minutes=45) <= time_until_event <= timedelta(hours=2, minutes=15) and event.status == 'scheduled':
            send_event_reminder_email.delay(
                user_email=user.email,
                user_name=f"{user.first_name} {user.last_name}".strip() or user.username,
                event_name=event.name,
                event_start_time=event.start_time.strftime('%Y-%m-%d %H:%M:%S UTC'),
                event_location=event.location
            )
            
            logger.info(f"Sent immediate reminder to {user.email} for new registration on event {event.name}")
            return f"Immediate reminder sent to {user.email}"
        else:
            logger.info(f"No immediate reminder needed for registration {registration_id} - event not within 2 hour window")
            return "No reminder needed - event not within 2 hour window"
            
    except Registration.DoesNotExist:
        logger.error(f"Registration {registration_id} not found")
        return "Registration not found"
    except Exception as e:
        logger.error(f"Error sending reminder for new registration {registration_id}: {str(e)}")
        raise e