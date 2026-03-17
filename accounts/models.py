from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class EmailOTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(default=timezone.now)
    is_verified = models.BooleanField(default=False)
    attempts = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} - {self.otp}"
