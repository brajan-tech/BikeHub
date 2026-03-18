from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from .models import EmailOTP
from .utils import generate_otp, send_otp_email
def client_register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        phone = request.POST.get("phone")

        # 🔒 Username duplicate check (MISSING FIX)
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect("client_register")

        # 🔒 Email duplicate check
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered")
            return redirect("client_register")

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            is_active=False
        )

        otp = generate_otp()
        EmailOTP.objects.create(user=user, otp=otp)

        try:
            send_otp_email(email, otp)
            messages.success(request, "OTP sent to your email.")
        except Exception:
            messages.error(request, "Failed to send OTP. Please check your email or try again later.")

        request.session["otp_user_id"] = user.id

        return redirect("verify_otp")

    return render(request, "auth/client_register.html")


from django.utils import timezone
from datetime import timedelta
def verify_otp(request):
    user_id = request.session.get("otp_user_id")
    if not user_id:
        return redirect("client_register")

    user = User.objects.get(id=user_id)
    otp_obj = EmailOTP.objects.filter(user=user, is_verified=False).last()

    if request.method == "POST":

        # 🔁 RESEND OTP
        if "resend_otp" in request.POST:
            otp = generate_otp()

            EmailOTP.objects.filter(user=user, is_verified=False).update(is_verified=True)

            EmailOTP.objects.create(user=user, otp=otp, attempts=0)

            send_otp_email(user.email, otp)

            messages.success(request, "New OTP sent to your email")
            return redirect("verify_otp")

        # ✅ VERIFY OTP
        entered_otp = request.POST.get("otp")

        if timezone.now() - otp_obj.created_at > timedelta(minutes=5):
            messages.error(request, "OTP expired. Please resend OTP.")
            return redirect("verify_otp")

        if otp_obj.attempts >= 3:
            messages.error(request, "Too many attempts. Please resend OTP.")
            return redirect("verify_otp")

        if otp_obj.otp == entered_otp:
            otp_obj.is_verified = True
            otp_obj.save()

            user.is_active = True
            user.save()

            messages.success(request, "Email verified successfully")
            return redirect("client_login")

        otp_obj.attempts += 1
        otp_obj.save()
        messages.error(request, "Invalid OTP")

    return render(request, "auth/verify_otp.html")
