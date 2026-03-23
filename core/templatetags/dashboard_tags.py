from django import template
from core.models import ServiceRequest
from parts.models import SparePart

register = template.Library()

@register.simple_tag
def get_dashboard_metrics():
    bikes_in_garage = ServiceRequest.objects.exclude(status='completed').count()
    low_stock_parts = SparePart.objects.filter(stock_quantity__lt=5).count()
    pending_services = ServiceRequest.objects.filter(status='pending').count()
    
    return {
        'bikes_in_garage': bikes_in_garage,
        'low_stock_parts': low_stock_parts,
        'pending_services': pending_services
    }
