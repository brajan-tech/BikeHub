from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.template.loader import get_template

from xhtml2pdf import pisa
from .models import Invoice

from parts.models import ServicePartUsage

from billing.utils import render_to_pdf


# -------------------------
# Invoice Detail (HTML)
# -------------------------

from billing.utils import calculate_parts_total

def invoice_detail(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)

    part_usages = ServicePartUsage.objects.filter(
        service_request=invoice.service_request
    )

    return render(request, "billing/invoice_detail.html", {
        "invoice": invoice,
        "part_usages": part_usages
    })


# -------------------------
# Invoice PDF
# -------------------------

def invoice_pdf(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)

    service = invoice.service_request

    part_usages = ServicePartUsage.objects.filter(
        service_request=service
    )

    return render_to_pdf(
        "billing/invoice_pdf.html",
        {
            "invoice": invoice,
            "part_usages": part_usages
        }
    )

