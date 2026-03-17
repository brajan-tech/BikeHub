from django.urls import path
from . import views

urlpatterns = [
    path("invoice/<int:invoice_id>/", views.invoice_detail, name="invoice_detail"),
    path("invoice/<int:invoice_id>/pdf/", views.invoice_pdf, name="invoice_pdf"),
]
