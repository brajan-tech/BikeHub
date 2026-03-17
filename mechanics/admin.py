from django.contrib import admin
from django.template.response import TemplateResponse
from datetime import date
import calendar

from .models import Mechanic, Attendance


# =========================
# Mechanic Admin
# =========================
@admin.register(Mechanic)
class MechanicAdmin(admin.ModelAdmin):
    autocomplete_fields = ("user",)
    list_display = ("id", "get_username", "phone")
    search_fields = ("user__username", "phone")
    list_filter = ("is_active",)

    def get_username(self, obj):
        return obj.user.username

    get_username.short_description = "Mechanic Name"


# =========================
# Attendance Admin
# =========================
from datetime import date
import calendar
from django.template.response import TemplateResponse
from django.urls import path
from django.contrib import admin
from .models import Mechanic, Attendance


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ("mechanic", "date", "status")
    list_filter = ("status", "date")

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "report/",
                self.admin_site.admin_view(self.monthly_report),
                name="attendance-report",
            ),
        ]
        return custom_urls + urls

    def monthly_report(self, request):
        today = date.today()
        month = int(request.GET.get("month", today.month))
        year = int(request.GET.get("year", today.year))

        total_days = calendar.monthrange(year, month)[1]
        sundays = sum(
            1 for day in range(1, total_days + 1)
            if date(year, month, day).weekday() == 6
            )
        working_days = total_days - sundays
        report_data = []
        for mechanic in Mechanic.objects.all():
            present_days = Attendance.objects.filter(
                mechanic=mechanic,
                date__year=year,
                date__month=month,
                status="Present"
                ).count()
            absent_days = working_days - present_days
            report_data.append({
                "mechanic": mechanic,
                "present": present_days,
                "absent": absent_days,
                "total": working_days
                })


        context = dict(
            self.admin_site.each_context(request),
            report_data=report_data,
            month=month,
            year=year
        )

        return TemplateResponse(request, "admin/attendance_report.html", context)

