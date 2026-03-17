from django.conf import settings
from django.core.mail import send_mail
from billing.models import Invoice
from core.models import EmailNotification


def send_service_completed_email(service_request):
    user = service_request.bike.user
    if not user or not user.email:
        return

    try:
        invoice = Invoice.objects.get(service_request=service_request)
    except Invoice.DoesNotExist:
        return

    message = f"""
Hello {user.first_name or user.username},

Your bike service has been completed successfully!

 Bike Details
----------------
Bike: {service_request.bike}
Status: {service_request.status}

Invoice Summary
----------------
Invoice No: {invoice.id}
Labour Charge: ₹{invoice.labour_charge}
Parts Total: ₹{invoice.parts_total}
----------------
GRAND TOTAL: ₹{invoice.grand_total}

Please visit BikeHub to view full invoice details.

Thank you for choosing BikeHub 
"""

    send_mail(
        subject="BikeHub – Service Completed & Invoice Summary",
        message=message,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[user.email],
    )

    EmailNotification.objects.create(
        user=user,
        subject="BikeHub – Service Completed & Invoice Summary",
        message="Invoice summary email sent",
        status="sent",
    )
