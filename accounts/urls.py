from django.urls import path
from .views import client_register, verify_otp

urlpatterns = [
    path("register/", client_register, name="client_register"),
    path("verify-otp/", verify_otp, name="verify_otp"),
]
