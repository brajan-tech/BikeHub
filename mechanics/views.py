from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta

from .models import Mechanic, Attendance
from core.models import ServiceRequest
from service.models import WorkProgress   # if used later
from django.contrib.admin.views.decorators import staff_member_required
import calendar

from django.db.models import Q
from mechanics.models import Attendance
# =========================
# MECHANIC LOGIN
# =========================
def employee_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            try:
                Mechanic.objects.get(user=user)
                login(request, user)
                return redirect('mechanic_attendance')
            except Mechanic.DoesNotExist:
                return render(request, 'mechanics/employee_login.html', {
                    'error': 'You are not registered as a mechanic'
                })
        else:
            return render(request, 'mechanics/employee_login.html', {
                'error': 'Invalid username or password'
            })

    return render(request, 'mechanics/employee_login.html')


# =========================
# ATTENDANCE
# =========================
@login_required
def mechanic_attendance(request):
    today = timezone.now().date()
    user = request.user

    attendance, created = Attendance.objects.get_or_create(
        mechanic=user,
        date=today
    )

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "checkin" and not attendance.check_in:
            attendance.check_in = timezone.now().time()
            attendance.status = "Present"
            attendance.save()

        elif action == "checkout" and attendance.check_in and not attendance.check_out:
            attendance.check_out = timezone.now().time()
            attendance.save()

        return redirect("mechanic_attendance")

    return render(request, "mechanics/attendance.html", {
        "attendance": attendance
    })


def attendance_completed(user):
    today = timezone.now().date()
    return Attendance.objects.filter(
        mechanic=user,
        date=today,
        check_in__isnull=False
    ).exists()


# =========================
# MECHANIC DASHBOARD
# =========================




@login_required
def mechanic_dashboard(request):
    mechanic = request.user.mechanic

    # -----------------------------
    # Attendance (today)
    # -----------------------------
    today = timezone.now().date()
    attendance = Attendance.objects.filter(
        mechanic=request.user,
        date=today
    ).first()

    if request.method == "POST":
        if attendance and attendance.check_in and not attendance.check_out:
            attendance.check_out = timezone.now().time()
            attendance.save()
            return redirect('mechanic_dashboard')

    # -----------------------------
    # AUTO HIDE COMPLETED (24 hrs)
    # -----------------------------
    now = timezone.now()
    cutoff_time = now - timedelta(hours=24)

    services = ServiceRequest.objects.filter(
        mechanic=mechanic
    ).filter(
        Q(status__in=['pending', 'assigned', 'in_progress']) |
        Q(status='completed', completed_at__gte=cutoff_time)
    ).order_by('-updated_at')

    # -----------------------------
    return render(request, "mechanics/dashboard.html", {
        "services": services,
        "attendance": attendance
    })


# =========================
# UPDATE WORK
# =========================
@login_required
def update_work(request, id):
    service = get_object_or_404(ServiceRequest, id=id)

    if request.method == 'POST':
        service.status = request.POST['status']

        if service.status == 'completed' and not service.completed_at:
            service.completed_at = timezone.now()

        if 'work_photo' in request.FILES:
            service.work_photo = request.FILES['work_photo']

        service.save()
        return redirect('mechanic_dashboard')

    return render(request, 'mechanics/update_work.html', {
        'service': service
    })

@login_required
def attendance_report(request):
    user = request.user

    # month & year (default = current)
    month = int(request.GET.get("month", timezone.now().month))
    year = int(request.GET.get("year", timezone.now().year))

    # total days in month
    total_days = calendar.monthrange(year, month)[1]

    # count Sundays
    sundays = 0
    for day in range(1, total_days + 1):
        if calendar.weekday(year, month, day) == 6:  # Sunday
            sundays += 1

    # present days
    present_days = Attendance.objects.filter(
        mechanic=user,
        date__year=year,
        date__month=month,
        status="Present"
    ).count()

    # working days
    working_days = total_days - sundays

    # absent days
    absent_days = working_days - present_days

    context = {
        "month_name": calendar.month_name[month],
        "year": year,
        "total_days": total_days,
        "sundays": sundays,
        "working_days": working_days,
        "present_days": present_days,
        "absent_days": absent_days,
    }

    return render(request, "mechanics/attendance_report.html", context)

@staff_member_required
def admin_attendance_report(request):

    month = int(request.GET.get("month", timezone.now().month))
    year = int(request.GET.get("year", timezone.now().year))
    mechanic_id = request.GET.get("mechanic")

    total_days = calendar.monthrange(year, month)[1]

    sundays = sum(
        1 for day in range(1, total_days + 1)
        if calendar.weekday(year, month, day) == 6
    )

    working_days = total_days - sundays

    mechanics = Mechanic.objects.all()
    report = []

    for mech in mechanics:
        if mechanic_id and str(mech.id) != mechanic_id:
            continue

        present = Attendance.objects.filter(
            mechanic=mech.user,
            date__year=year,
            date__month=month,
            status="Present"
        ).count()

        absent = working_days - present

        report.append({
            "name": mech.user.username,
            "present": present,
            "absent": absent
        })

    months = [
        (1,"January"), (2,"February"), (3,"March"), (4,"April"),
        (5,"May"), (6,"June"), (7,"July"), (8,"August"),
        (9,"September"), (10,"October"), (11,"November"), (12,"December")
    ]

    context = {
        "month": month,
        "year": year,
        "month_name": calendar.month_name[month],
        "total_days": total_days,
        "sundays": sundays,
        "working_days": working_days,
        "report": report,
        "mechanics": mechanics,
        "selected_mechanic": mechanic_id,
        "months": months,
        "years": range(2023, 2031),
    }
from core.services import send_service_completed_email

def complete_service(request, service_id):
    service = ServiceRequest.objects.get(id=service_id)
    service.mark_completed()

    send_service_completed_email(service)

    return redirect("dashboard")

    return render(request, "mechanics/admin_attendance_report.html", context)




