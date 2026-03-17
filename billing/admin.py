from django.contrib import admin
from .models import Invoice, InvoicePart


# -----------------------------
# Inline for Invoice Parts
# -----------------------------
class InvoicePartInline(admin.TabularInline):
    model = InvoicePart
    extra = 1


# -----------------------------
# Invoice Admin (FINAL FIXED)
# -----------------------------
@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "service_request",
        "labour_charge",
        "parts_total",
        "grand_total",
        "created_at",
    )

    search_fields = (
        "service_request__bike__bike_number",
        "service_request__bike__bike_name",
        "service_request__status",
    )

    list_editable = ("labour_charge",)

    readonly_fields = (
        "parts_total",
        "grand_total",
    )

    inlines = [InvoicePartInline]

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        obj.calculate_totals()
