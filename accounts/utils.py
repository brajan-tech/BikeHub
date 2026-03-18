import random

def generate_otp():
    return str(random.randint(100000, 999999))
from django.core.mail import send_mail
from django.conf import settings

import logging
logger = logging.getLogger(__name__)

def send_otp_email(email, otp):
    try:
        send_mail(
            subject="BikeHub Email Verification",
            message=f"Your OTP is {otp}. Valid for 5 minutes.",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
            fail_silently=False,
        )
    except Exception as e:
        logger.error(f"Error sending OTP email to {email}: {str(e)}")
        # We don't re-raise the exception to avoid 500 error, 
        # but the user won't receive the OTP.
        pass
