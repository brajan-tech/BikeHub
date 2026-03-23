from django.urls import path
from . import views
from .views import client_bikes, client_bike_history
urlpatterns = [

    # =========================
    # HOME & AUTH
    # =========================
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),

    # =========================
    # LOGIN SELECTION
    # =========================
    path('select-login/', views.select_login, name='select_login'),
    path('client-login/', views.client_login, name='client_login'),
    path('employee-login/', views.employee_login, name='employee_login'),
    path('client-register/', views.client_register, name='client_register'),

    # =========================
    # BIKE
    # =========================
    path('add-bike/', views.add_bike, name='add_bike'),

    # =========================
    # ADMIN SERVICES
    # =========================
    path('admin/services/', views.admin_service_list, name='admin_services'),
    path(
        'admin/assign/<int:service_id>/',
        views.assign_mechanic,
        name='assign_mechanic'
    ),

    # =========================
    # CLIENT
    # =========================
    path('client-dashboard/', views.client_dashboard, name='client_dashboard'),
    path('book-service/', views.book_service, name='book_service'),
    path('select-login/', views.select_login, name='select_login'),
    path("client/bikes/", client_bikes, name="client_bikes"),
    path("client/bike/<int:bike_id>/history/", client_bike_history, name="client_bike_history"),
    path("client/feedback/<int:service_id>/", views.submit_feedback, name="submit_feedback"),

]
