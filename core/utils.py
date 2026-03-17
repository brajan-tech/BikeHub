from django.core.mail import send_mail
from django.utils import timezone
from .models import EmailNotification
from django.conf import settings

def send_notification_email(notification_id):
    notification = EmailNotification.objects.get(id=notification_id)

    try:
        send_mail(
            subject=notification.subject,
            message=notification.message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[notification.user.email],
            fail_silently=False,
        )

        notification.status = "sent"
        notification.sent_at = timezone.now()
        notification.save()

    except Exception as e:
        print("EMAIL ERROR:", e)
        notification.status = "failed"
        notification.save()

