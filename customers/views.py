from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from core.models import ServiceRequest
from service.models import WorkProgress
from billing.models import Invoice


# =========================
# MY SERVICES
# =========================
@login_required
def my_services(request):
    services = ServiceRequest.objects.filter(
        user=request.user
    )
    return render(
        request,
        'customers/my_services.html',
        {'services': services}
    )


# =========================
# MY INVOICES
# =========================
@login_required
def my_invoices(request):
    invoices = Invoice.objects.filter(
        service_request__user=request.user
    ).select_related('service_request')
    return render(
        request,
        'customers/my_invoices.html',
        {'invoices': invoices}
    )


# =========================
# CLIENT DASHBOARD
# =========================
@login_required
def client_dashboard(request):
    services = ServiceRequest.objects.filter(user=request.user)

    # ✅ Attach invoice directly to each service (SAFE METHOD)
    for service in services:
        service.invoice = Invoice.objects.filter(
            service_request=service
        ).first()

    return render(
        request,
        'customers/client_dashboard.html',
        {'services': services}
    )
