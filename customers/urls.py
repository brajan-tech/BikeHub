from django.urls import path
from .views import my_services
from .views import my_invoices
urlpatterns = [
    path('my-services/', my_services, name='my_services'),
     path('invoices/', my_invoices, name='my_invoices'),
]
