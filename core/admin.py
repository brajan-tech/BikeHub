from django.contrib import admin
from django.urls import path, reverse
from django.template.response import TemplateResponse
from django.utils.html import format_html

from .models import Bike, ServiceRequest
from billing.models import Invoice

from django.db.models import Sum, Count
from datetime import date

from parts.models import ServicePartUsage

from django.utils import timezone

from django.contrib import admin
from .models import ServiceRequest
# =====================================================
# Bike Admin (Service History inside Admin)
# =====================================================
from django.contrib import admin
from django.urls import path
from django.template.response import TemplateResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
# First unregister default User admin
admin.site.unregister(User)

# Register again with search enabled
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    search_fields = ("username", "first_name", "last_name", "email")
@admin.register(Bike)
class BikeAdmin(admin.ModelAdmin):
    autocomplete_fields = ("user",) 
    list_display = ("bike_name", "bike_number", "user")

    search_fields = ("bike_name", "bike_number")  # ✅ THIS LINE

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "<int:bike_id>/history/",
                self.admin_site.admin_view(self.bike_history_view),
                name="bike-history",
            )
        ]
        return custom_urls + urls

    def bike_history_view(self, request, bike_id):
        bike = get_object_or_404(Bike, id=bike_id)

        services = ServiceRequest.objects.filter(
            bike=bike
        ).select_related("mechanic").order_by("-created_at")

        history = []

        for s in services:
            history.append({
                "date": s.created_at,
                "problem": s.problem_description or "Not mentioned",
                "mechanic": s.mechanic,
                "status": s.status,
                "parts": s.part_usages.all(),  # ✅ IMPORTANT
            })

        context = dict(
            self.admin_site.each_context(request),
            bike=bike,
            history=history,
        )

        return TemplateResponse(
            request,
            "admin/bike_history.html",
            context,
        )


    from django.template.response import TemplateResponse
from django.shortcuts import get_object_or_404

def bike_history_view(self, request, bike_id):
    bike = get_object_or_404(Bike, id=bike_id)

    services = ServiceRequest.objects.filter(
        bike=bike
    ).select_related("mechanic").order_by("-created_at")

    history = []

    for s in services:
        problem_text = s.problem_description or "Not mentioned"

        # ✅ correct related_name
        parts = s.part_usages.all()

        history.append({
            "date": s.created_at,
            "problem": problem_text,
            "mechanic": s.mechanic,
            "status": s.status,
            "parts": parts,
        })

    context = dict(
        self.admin_site.each_context(request),
        bike=bike,
        history=history,
    )

    return TemplateResponse(
        request,
        "admin/bike_history.html",
        context,
    )


# =====================================================
# Service Request Admin
# =====================================================

@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):

    # ✅ THIS is what autocomplete uses
    search_fields = (
        "bike__bike_name",
        "bike__bike_number",
    )

    list_display = ("bike", "status", "created_at")
    list_filter = ("status", "mechanic")

    fields = (
        'status',
        'user',
        'bike',
        'mechanic',
        'problem_description',
        'labour_charge',
        'work_photo',
        'completed_at',
    )

    readonly_fields = ('completed_at',)



    def save_model(self, request, obj, form, change):
        # ✅ set completed_at only once
        if obj.status == 'completed' and obj.completed_at is None:
            obj.completed_at = timezone.now()

        super().save_model(request, obj, form, change)

        # 🔥 sync invoice labour charge if invoice exists
        try:
            invoice = Invoice.objects.get(service_request=obj)
            invoice.labour_charge = obj.labour_charge
            invoice.save()
        except Invoice.DoesNotExist:
            pass

class MonthlyReportAdmin(admin.ModelAdmin):
    change_list_template = "admin/monthly_report.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "monthly-report/",
                self.admin_site.admin_view(self.monthly_report),
                name="monthly-report",
            )
        ]
        return custom_urls + urls
    

    def monthly_report(self, request):
        month = int(request.GET.get("month", date.today().month))
        year = int(request.GET.get("year", date.today().year))

        completed = ServiceRequest.objects.filter(
            status="completed",
            created_at__month=month,
            created_at__year=year
        )

        total_bikes = completed.count()

        total_labour = completed.aggregate(
            total=Sum("labour_charge")
        )["total"] or 0

        total_spares = ServicePartUsage.objects.filter(
            service_request__in=completed
        ).aggregate(
            total=Sum("total_price")
        )["total"] or 0

        mechanic_stats = completed.values(
            "mechanic__user__username"
        ).annotate(
            bikes=Count("id"),
            labour=Sum("labour_charge")
        )

        context = dict(
            self.admin_site.each_context(request),
            month=month,
            year=year,
            total_bikes=total_bikes,
            total_labour=total_labour,
            total_spares=total_spares,
            total_revenue=total_labour + total_spares,
            mechanic_stats=mechanic_stats,
            title="Monthly Revenue Report",
        )

        return TemplateResponse(request, "admin/monthly_report.html", context)

from django.contrib import admin
from .models import EmailNotification

@admin.register(EmailNotification)
class EmailNotificationAdmin(admin.ModelAdmin):
    list_display = ("user", "subject", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("user__username", "subject")


# =====================================================
# Admin Branding
# =====================================================
admin.site.site_header = "BikeHub Administration"
admin.site.site_title = "BikeHub Admin Portal"
admin.site.index_title = "Welcome to BikeHub Dashboard"

from .models import Feedback

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ("service_request", "rating", "is_public", "created_at")
    list_filter = ("rating", "is_public", "created_at")
    search_fields = ("service_request__bike__bike_number", "comment")

from .models import Enquiry

from django.utils.html import format_html

@admin.register(Enquiry)
class EnquiryAdmin(admin.ModelAdmin):
    list_display = ("name", "call_prospect", "created_at")
    search_fields = ("name", "phone_number", "message")
    actions = ["mark_completed"]
    readonly_fields = ("call_customer",)
    fields = ("name", "phone_number", "call_customer", "message")

    @admin.display(description="Direct Call")
    def call_customer(self, obj):
        if obj and obj.phone_number:
            return format_html(
                '<a href="tel:{}" style="display:inline-block; background-color:#3b82f6; color:white; padding:8px 16px; border-radius:6px; font-weight:bold; text-decoration:none; font-size: 14px; box-shadow: 0 4px 6px rgba(59,130,246,0.3);">📞 Click to Call {}</a>', 
                obj.phone_number, obj.phone_number
            )
        return ""

    @admin.display(description="Phone Number")
    def call_prospect(self, obj):
        return format_html(
            '<a href="tel:{}" style="display:inline-block; background-color:#22c55e; color:white; padding:4px 10px; border-radius:4px; font-weight:bold; text-decoration:none;">📞 Call {}</a>', 
            obj.phone_number, obj.phone_number
        )

    @admin.action(description="Mark selected as Completed (Deletes them)")
    def mark_completed(self, request, queryset):
        count = queryset.count()
        queryset.delete()
        self.message_user(request, f"{count} enquiries marked as completed and deleted.")
