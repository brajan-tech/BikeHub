from django.db.models.signals import post_save
from django.dispatch import receiver

from core.models import ServiceRequest, EmailNotification
from billing.models import Invoice
from core.services import send_service_completed_email


@receiver(post_save, sender=ServiceRequest)
def auto_email_on_service_complete(sender, instance, created, **kwargs):
    # only when completed
    if instance.status != "completed":
        return

    # invoice iruka?
    if not Invoice.objects.filter(service_request=instance).exists():
        return

    # already email sent ah?
    already_sent = EmailNotification.objects.filter(
        user=instance.bike.user,
        subject__icontains="Service Completed & Invoice"
    ).exists()

    if already_sent:
        return

    send_service_completed_email(instance)
