from django.contrib import admin, messages
from .models import SparePart, ServicePartUsage
from core.models import ServiceRequest


# =========================
# Spare Part Admin
# =========================

from django.contrib import admin, messages
from django.db.models import Case, When, Value, IntegerField
from .models import SparePart


@admin.register(SparePart)
class SparePartAdmin(admin.ModelAdmin):
    list_display = ("name", "stock_quantity", "price", "stock_status")
    search_fields = ("name",)

    # 🔼 LOW stock items first
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(
            stock_priority=Case(
                When(stock_quantity__lte=5, then=Value(0)),
                default=Value(1),
                output_field=IntegerField(),
            )
        ).order_by("stock_priority", "stock_quantity")

    # ⚠️ STOCK STATUS COLUMN
    def stock_status(self, obj):
        if obj.stock_quantity <= 5:
            return "⚠ LOW"
        return "OK"

    stock_status.short_description = "Stock Status"

    # 🔥 TOP WARNING MESSAGE (THIS IS THE KEY)
    def changelist_view(self, request, extra_context=None):
        low_stock_parts = SparePart.objects.filter(stock_quantity__lte=5)

        if low_stock_parts.exists():
            names = ", ".join(
                f"{p.name} ({p.stock_quantity})"
                for p in low_stock_parts
            )
            messages.warning(
                request,
                f"⚠ LOW STOCK ALERT: {names}"
            )

        return super().changelist_view(request, extra_context)


# =========================
# Service Part Usage Admin
# =========================
@admin.register(ServicePartUsage)
class ServicePartUsageAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "service_request",
        "spare_part",
        "quantity_used",
        "price_per_piece",
        "total_price",
    )
    autocomplete_fields = (
        "service_request",
        "spare_part",
    )

    

    readonly_fields = (
        "price_per_piece",
        "total_price",
    )

    def save_model(self, request, obj, form, change):
        # ✅ BASIC VALIDATIONS
        if not obj.service_request_id:
            messages.error(request, "Please select service request")
            return

        if not obj.spare_part:
            messages.error(request, "Please select spare part")
            return

        spare = obj.spare_part

        if spare.stock_quantity < obj.quantity_used:
            messages.error(
                request,
                f"Not enough stock for {spare.name}"
            )
            return

        # 🔗 AUTO LINK PRICE FROM SPARE PART
        obj.price_per_piece = spare.price
        obj.total_price = obj.price_per_piece * obj.quantity_used

        # 🔴 STOCK MINUS (ONLY ON CREATE)
        if not change:
            spare.stock_quantity -= obj.quantity_used
            spare.save()

        # ✅ SAVE SERVICE PART USAGE
        super().save_model(request, obj, form, change)

        # ⚠️ LOW STOCK WARNING
        if spare.stock_quantity <= 5:
            messages.warning(
                request,
                f"⚠ Stock low: {spare.name} (only {spare.stock_quantity} left)"
            )


