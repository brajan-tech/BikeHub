from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.contrib.auth.models import User

from .models import Attendance, Mechanic


@receiver(post_save, sender=User)
def create_attendance_for_mechanic(sender, instance, created, **kwargs):
    if created:
        # check this user is a mechanic
        if Mechanic.objects.filter(user=instance).exists():
            Attendance.objects.create(
                mechanic=instance,
                date=timezone.now().date(),
                status='Present'
            )
