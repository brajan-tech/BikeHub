import random

def generate_otp():
    return str(random.randint(100000, 999999))
from django.core.mail import send_mail
from django.conf import settings

import logging
logger = logging.getLogger(__name__)

def send_otp_email(email, otp):
    text_message = f"Your OTP is {otp}. Valid for 5 minutes."
    
    html_message = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; border: 1px solid #e2e8f0; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
        <div style="background: linear-gradient(90deg, #22c55e, #3b82f6); padding: 25px; text-align: center;">
            <h1 style="color: white; margin: 0; font-size: 24px;">BikeHub Verification</h1>
        </div>
        <div style="padding: 30px; background: #ffffff;">
            <p style="font-size: 16px; color: #334155;">Hello,</p>
            <p style="font-size: 16px; color: #334155;">Please use the verification code below to complete your registration process.</p>
            <div style="text-align: center; margin: 30px 0;">
                <span style="display: inline-block; background: #f8fafc; border: 2px dashed #94a3b8; padding: 15px 30px; font-size: 32px; font-weight: bold; color: #0f172a; letter-spacing: 5px;">{otp}</span>
            </div>
            <p style="font-size: 14px; color: #64748b; text-align: center;">This code is valid for 5 minutes.</p>
        </div>
        <div style="background: #f8fafc; padding: 15px; text-align: center; border-top: 1px solid #e2e8f0;">
            <p style="font-size: 12px; color: #94a3b8; margin: 0;">© 2026 BikeHub Ecosystem. Precision. Performance. Passion.</p>
        </div>
    </div>
    """

    try:
        send_mail(
            subject="BikeHub Email Verification",
            message=text_message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
            fail_silently=False,
            html_message=html_message
        )
    except Exception as e:
        logger.error(f"Error sending OTP email to {email}: {str(e)}")
        # We don't re-raise the exception to avoid 500 error, 
        # but the user won't receive the OTP.
        pass
