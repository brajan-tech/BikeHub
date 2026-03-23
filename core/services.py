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

    try:
        send_mail(
            subject="BikeHub – Service Completed & Invoice Summary",
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user.email],
            html_message=f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; border: 1px solid #e2e8f0; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
                <div style="background: linear-gradient(90deg, #22c55e, #3b82f6); padding: 25px; text-align: center;">
                    <h1 style="color: white; margin: 0; font-size: 24px;">Service Completed</h1>
                </div>
                <div style="padding: 30px; background: #ffffff;">
                    <p style="font-size: 16px; color: #334155; font-weight: bold;">Hello {user.first_name or user.username},</p>
                    <p style="font-size: 16px; color: #334155;">Your bike service has been completed successfully! Here is your invoice summary:</p>
                    
                    <div style="background: #f8fafc; border-radius: 8px; padding: 20px; margin: 20px 0;">
                        <h3 style="margin-top: 0; color: #0f172a; border-bottom: 2px solid #e2e8f0; padding-bottom: 10px;">Bike Details</h3>
                        <p style="margin: 5px 0; color: #475569;"><strong>Bike:</strong> {service_request.bike}</p>
                        <p style="margin: 5px 0; color: #475569;"><strong>Status:</strong> <span style="background: #22c55e; color: white; padding: 2px 8px; border-radius: 4px; font-weight: bold; font-size: 12px; text-transform: uppercase;">{service_request.status}</span></p>
                        
                        <h3 style="margin-top: 20px; color: #0f172a; border-bottom: 2px solid #e2e8f0; padding-bottom: 10px;">Invoice Summary</h3>
                        <table style="width: 100%; border-collapse: collapse; color: #475569;">
                            <tr><td style="padding: 5px 0;">Invoice No:</td><td style="text-align: right; font-weight: bold;">#{invoice.id}</td></tr>
                            <tr><td style="padding: 5px 0;">Labour Charge:</td><td style="text-align: right;">₹{invoice.labour_charge}</td></tr>
                            <tr><td style="padding: 5px 0; border-bottom: 1px solid #e2e8f0;">Parts Total:</td><td style="text-align: right; border-bottom: 1px solid #e2e8f0;">₹{invoice.parts_total}</td></tr>
                            <tr><td style="padding: 15px 0 5px 0; font-weight: bold; font-size: 18px; color: #0f172a;">GRAND TOTAL:</td><td style="text-align: right; font-weight: bold; font-size: 18px; color: #22c55e;">₹{invoice.grand_total}</td></tr>
                        </table>
                    </div>
                    
                    <p style="font-size: 14px; color: #64748b; text-align: center; margin-top: 30px;">Please visit the BikeHub app to view full invoice details.</p>
                </div>
                <div style="background: #f8fafc; padding: 15px; text-align: center; border-top: 1px solid #e2e8f0;">
                    <p style="font-size: 12px; color: #94a3b8; margin: 0;">© 2026 BikeHub Ecosystem. Precision. Performance. Passion.</p>
                </div>
            </div>
            """
        )
        status = "sent"
    except Exception:
        status = "failed"

    EmailNotification.objects.create(
        user=user,
        subject="BikeHub – Service Completed & Invoice Summary",
        message="Invoice summary email sent",
        status=status,
    )
