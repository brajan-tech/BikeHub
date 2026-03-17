from django.db import models
from django.contrib.auth.models import User

class Mechanic(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.user.username

class Attendance(models.Model):
    mechanic = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'is_staff': True}
    )
    date = models.DateField(auto_now_add=True)
    check_in = models.TimeField(null=True, blank=True)
    check_out = models.TimeField(null=True, blank=True)
    status = models.CharField(
        max_length=10,
        choices=[('Present', 'Present'), ('Absent', 'Absent')],
        default='Present'
    )

    def __str__(self):
        return f"{self.mechanic.username} - {self.date}"
class AttendanceReport(models.Model):
    class Meta:
        managed = False   # DB table create aagathu
        verbose_name = "Attendance Report"
        verbose_name_plural = "Attendance Reports"
