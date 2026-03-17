from django.db.models.signals import post_save
from django.dispatch import receiver

from core.models import ServiceRequest, EmailNotification
from billing.models import Invoice
from core.services import send_service_completed_email


# --------------------------------------------------
# 1️⃣ Sync labour charge when ServiceRequest updates
# --------------------------------------------------
@receiver(post_save, sender=ServiceRequest)
def sync_invoice_labour_charge(sender, instance, **kwargs):
    try:
        invoice = Invoice.objects.get(service_request=instance)
        invoice.labour_charge = instance.labour_charge
        invoice.calculate_totals()
        invoice.save()
    except Invoice.DoesNotExist:
        pass


# --------------------------------------------------
# 2️⃣ Send email automatically when Invoice is CREATED
# --------------------------------------------------
@receiver(post_save, sender=Invoice)
@receiver(post_save, sender=Invoice)
def send_email_on_invoice_create(sender, instance, created, **kwargs):
    if not created:
        return

    service = instance.service_request

    if service.status != "completed":
        return

    # ✅ check email already sent for THIS service
    already_sent = EmailNotification.objects.filter(
        message__icontains=f"Service ID: {service.id}"
    ).exists()

    if already_sent:
        return

    send_service_completed_email(service)

