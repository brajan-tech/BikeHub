from django.urls import path
from .views import bike_history

urlpatterns = [
    path("bike-history/", bike_history, name="bike_history"),
]
