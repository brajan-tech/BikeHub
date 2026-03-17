from django.db import models


class MonthlyRevenueReport(models.Model):
    class Meta:
        verbose_name = "Monthly Revenue Report"
        verbose_name_plural = "Revenue Reports"

    def __str__(self):
        return "Monthly Revenue Report"


class MonthlyAttendanceReport(models.Model):
    class Meta:
        verbose_name = "Monthly Attendance Report"
        verbose_name_plural = "Attendance Reports"

