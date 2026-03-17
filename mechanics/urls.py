from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.employee_login, name='employee_login'),
    path('attendance/', views.mechanic_attendance, name='mechanic_attendance'),
    path('dashboard/', views.mechanic_dashboard, name='mechanic_dashboard'),
    path('update-work/<int:id>/', views.update_work, name='update_work'),
    path("attendance/report/", views.attendance_report, name="attendance_report"),
    path("admin/attendance/report/", views.admin_attendance_report,name="admin_attendance_report"),


]
