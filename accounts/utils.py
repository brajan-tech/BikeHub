import random

def generate_otp():
    return str(random.randint(100000, 999999))
from django.core.mail import send_mail
from django.conf import settings

def send_otp_email(email, otp):
    send_mail(
        subject="BikeHub Email Verification",
        message=f"Your OTP is {otp}. Valid for 5 minutes.",
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[email],
        fail_silently=False,
    )
