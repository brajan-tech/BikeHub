from django.contrib import admin
from django.urls import path
from django.template.response import TemplateResponse
from datetime import date
import calendar

from .models import MonthlyRevenueReport, MonthlyAttendanceReport
from mechanics.models import Attendance, Mechanic


from .models import MonthlyAttendanceReport

from billing.models import Invoice

from django.db.models import Sum, Count

from mechanics.models import Mechanic, Attendance



from django.shortcuts import redirect





@admin.register(MonthlyAttendanceReport)
class MonthlyAttendanceReportAdmin(admin.ModelAdmin):

    # -----------------------------
    # Custom URL
    # -----------------------------
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "monthlyattendancereport/",
                self.admin_site.admin_view(self.attendance_report),
                name="monthly-attendance-report",
            )
        ]
        return custom_urls + urls

    # -----------------------------
    # Redirect model list → report
    # -----------------------------
    def changelist_view(self, request, extra_context=None):
        return redirect("admin:monthly-attendance-report")

    # -----------------------------
    # Report view
    # -----------------------------
    def attendance_report(self, request):

        # Filters
        month = int(request.GET.get("month", date.today().month))
        year = int(request.GET.get("year", date.today().year))
        selected_mechanic = request.GET.get("mechanic")

        # Dropdown data
        months = [(i, calendar.month_name[i]) for i in range(1, 13)]
        years = range(year - 5, year + 31)

        # Attendance queryset
        qs = Attendance.objects.filter(
            date__year=year,
            date__month=month
        )

        # Month summary
        total_days = calendar.monthrange(year, month)[1]
        sundays = sum(
            1 for d in range(1, total_days + 1)
            if date(year, month, d).weekday() == 6
        )
        working_days = total_days - sundays

        # Decide mechanics list
        if selected_mechanic:
            mechanics = Mechanic.objects.filter(
                id=int(selected_mechanic)
            ).select_related("user")

            qs = qs.filter(mechanic=mechanics.first().user)
        else:
            mechanics = Mechanic.objects.select_related("user")

        # Build report
        report = []
        for mech in mechanics:
            mech_qs = qs.filter(mechanic=mech.user)

            present = mech_qs.filter(status="Present").count()
            absent = working_days - present

            report.append({
                "mechanic": mech.user.username,
                "present": present,
                "absent": absent,
            })

        # Context
        context = dict(
            self.admin_site.each_context(request),
            title="Monthly Attendance Report",
            months=months,
            years=years,
            mechanics=mechanics,
            selected_month=month,
            year=year,
            selected_mechanic=selected_mechanic,
            report=report,
            total_days=total_days,
            sundays=sundays,
            working_days=working_days,
        )

        return TemplateResponse(
            request,
            "reports/admin_attendance_report.html",
            context,
        )




    
# =========================
# Monthly Revenue Report
# =========================


@admin.register(MonthlyRevenueReport)
class MonthlyRevenueReportAdmin(admin.ModelAdmin):

    # ✅ URL mapping
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "",
                self.admin_site.admin_view(self.monthly_report),
                name="monthly-revenue-report",
            )
        ]
        return custom_urls + urls

    # ✅ THIS METHOD WAS MISSING → now added
    def monthly_report(self, request):

        selected_month = int(request.GET.get("month", date.today().month))
        year = int(request.GET.get("year", date.today().year))

        months = [(i, calendar.month_name[i]) for i in range(1, 13)]

        invoices = Invoice.objects.filter(
            created_at__year=year,
            created_at__month=selected_month
        )

        total_bikes = invoices.count()

        total_labour = invoices.aggregate(
            total=Sum("labour_charge")
        )["total"] or 0

        total_spare = invoices.aggregate(
            total=Sum("parts_total")
        )["total"] or 0

        total_revenue = total_labour + total_spare

        mechanic_data = (
            invoices
            .values("service_request__mechanic__user__username")
            .annotate(
                bikes_done=Count("id"),
                labour_revenue=Sum("labour_charge")
            )
        )

        context = dict(
            self.admin_site.each_context(request),
            title="Monthly Revenue Report",
            months=months,
            selected_month=selected_month,
            year=year,
            total_bikes=total_bikes,
            total_labour=total_labour,
            total_spare=total_spare,
            total_revenue=total_revenue,
            mechanic_data=mechanic_data,
        )

        return TemplateResponse(
            request,
            "admin/monthly_revenue_report.html",
            context
        )




