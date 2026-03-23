
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from .models import Bike, ServiceRequest
from mechanics.models import Mechanic
from django.contrib.admin.views.decorators import staff_member_required

# =========================
# COMMON / HOME
# =========================

def home(request):
    from .models import Feedback, Enquiry
    from django.contrib import messages
    
    if request.method == "POST":
        name = request.POST.get('name')
        phone = request.POST.get('phone_number')
        message = request.POST.get('message')
        Enquiry.objects.create(name=name, phone_number=phone, message=message)
        messages.success(request, "Your enquiry has been submitted. We will call you back shortly!")
        return redirect('home')

    reviews = Feedback.objects.filter(is_public=True, rating__gte=4).order_by('-created_at')[:3]
    return render(request, 'core/home.html', {'reviews': reviews})


def logout_view(request):
    logout(request)
    return redirect('login')


# =========================
# AUTHENTICATION
# =========================

def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('home')

        return render(request, 'core/login.html', {
            'error': 'Invalid username or password'
        })

    return render(request, 'core/login.html')


def register_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        if User.objects.filter(username=username).exists():
            return render(request, 'core/register.html', {
                'error': 'Username already exists'
            })

        User.objects.create_user(username=username, password=password)
        return redirect('login')

    return render(request, 'core/register.html')


# =========================
# BIKE
# =========================

@login_required
def add_bike(request):
    if request.method == 'POST':
        bike_name = request.POST['bike_name']
        bike_number = request.POST['bike_number']

        Bike.objects.create(
            user=request.user,   # 🔑 important
            bike_name=bike_name,
            bike_number=bike_number
        )

        return redirect('client_dashboard')

    return render(request, 'core/add_bike.html')

# =========================
# LOGIN SELECTION
# =========================
def login_view(request):
    if request.method == 'POST':
        user = authenticate(
            request,
            username=request.POST['username'],
            password=request.POST['password']
        )

        if user:
            login(request, user)

            if user.is_superuser:
                return redirect('/admin/')
            else:
                return redirect('client_dashboard')

        return render(request, 'core/login.html', {
            'error': 'Invalid username or password'
        })

    return render(request, 'core/login.html')



def select_login(request):
    return render(request, 'auth/select_login.html')


def client_login(request):
    if request.method == "POST":
        user = authenticate(
            username=request.POST['username'],
            password=request.POST['password']
        )

        if user:
            login(request, user)
            return redirect('client_dashboard')

    return render(request, 'auth/client_login.html')


def employee_login(request):
    if request.method == "POST":
        user = authenticate(
            username=request.POST['username'],
            password=request.POST['password']
        )

        if user and Mechanic.objects.filter(user=user).exists():
            login(request, user)
            return redirect('mechanic_dashboard')

    return render(request, 'auth/employee_login.html')


def client_register(request):
    if request.method == "POST":
        if not User.objects.filter(username=request.POST['username']).exists():
            User.objects.create_user(
                username=request.POST['username'],
                email=request.POST['email'],
                password=request.POST['password']
            )
            return redirect('client_login')

    return render(request, 'auth/client_register.html')


# =========================
# CLIENT DASHBOARD & SERVICE
# =========================

@login_required
def client_dashboard(request):
    services = ServiceRequest.objects.filter(user=request.user).order_by('-id')

    return render(request, 'client/dashboard.html', {
        'services': services
    })



@login_required
def book_service(request):
    bikes = Bike.objects.filter(user=request.user)  # 🔑 own bikes only

    if request.method == 'POST':
        bike_id = request.POST['bike']
        problem = request.POST['problem']

        bike = Bike.objects.get(id=bike_id)

        ServiceRequest.objects.create(
            user=request.user,
            bike=bike,
            problem_description=problem
        )

        return redirect('client_dashboard')

    return render(request, 'client/book_service.html', {
        'bikes': bikes
    })


@staff_member_required
def admin_service_list(request):
    services = ServiceRequest.objects.all()
    mechanics = Mechanic.objects.all()

    return render(request, 'core/admin_service_list.html', {
        'services': services,
        'mechanics': mechanics
    })
@staff_member_required
def assign_mechanic(request, service_id):
    service = ServiceRequest.objects.get(id=service_id)

    if request.method == 'POST':
        mechanic_id = request.POST['mechanic']
        mechanic = Mechanic.objects.get(id=mechanic_id)

        service.mechanic = mechanic
        service.status = 'assigned'
        service.save()

    return redirect('admin_services')


# =========================
# LOGIN SELECTION
# =========================
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            # 🔑 ROLE BASED REDIRECT
            if user.is_superuser:
                return redirect('/admin/')
            else:
                return redirect('/client-dashboard/')
        else:
            return render(request, 'core/login.html', {
                'error': 'Invalid username or password'
            })

    return render(request, 'core/login.html')


def select_login(request):
    return render(request, 'auth/select_login.html')


def client_login(request):
    if request.method == "POST":
        user = authenticate(
            username=request.POST['username'],
            password=request.POST['password']
        )

        if user:
            login(request, user)
            return redirect('client_dashboard')

    return render(request, 'auth/client_login.html')


def employee_login(request):
    if request.method == "POST":
        user = authenticate(
            username=request.POST['username'],
            password=request.POST['password']
        )

        if user and Mechanic.objects.filter(user=user).exists():
            login(request, user)
            return redirect('mechanic_dashboard')

    return render(request, 'auth/employee_login.html')


def client_register(request):
    if request.method == "POST":
        if not User.objects.filter(username=request.POST['username']).exists():
            User.objects.create_user(
                username=request.POST['username'],
                email=request.POST['email'],
                password=request.POST['password']
            )
            return redirect('client_login')

    return render(request, 'auth/client_register.html')


# =========================
# CLIENT DASHBOARD & SERVICE
# =========================

@login_required
def client_dashboard(request):
    services = ServiceRequest.objects.filter(user=request.user).order_by('-id')

    return render(request, 'client/dashboard.html', {
        'services': services
    })



@login_required
def book_service(request):
    bikes = Bike.objects.filter(user=request.user)  # 🔑 own bikes only

    if request.method == 'POST':
        bike_id = request.POST['bike']
        problem = request.POST['problem']

        bike = Bike.objects.get(id=bike_id)

        ServiceRequest.objects.create(
            user=request.user,
            bike=bike,
            problem_description=problem
        )

        return redirect('client_dashboard')

    return render(request, 'client/book_service.html', {
        'bikes': bikes
    })


@staff_member_required
def admin_service_list(request):
    services = ServiceRequest.objects.all()
    mechanics = Mechanic.objects.all()

    return render(request, 'core/admin_service_list.html', {
        'services': services,
        'mechanics': mechanics
    })
@staff_member_required
def assign_mechanic(request, service_id):
    service = ServiceRequest.objects.get(id=service_id)

    if request.method == 'POST':
        mechanic_id = request.POST['mechanic']
        mechanic = Mechanic.objects.get(id=mechanic_id)

        service.mechanic = mechanic
        service.status = 'assigned'
        service.save()

    return redirect('admin_services')
from django.contrib.auth.models import User
from customers.models import CustomerProfile

def register_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        phone = request.POST['phone']

        user = User.objects.create_user(
            username=username,
            password=password
        )

        # ✅ CREATE PROFILE WITH PHONE
        CustomerProfile.objects.create(
            user=user,
            phone=phone
        )

    if user.is_staff:
        return redirect('mechanic_attendance')
    else:
        return redirect('home')


    return render(request, 'core/register.html')



from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from core.models import Bike, ServiceRequest
from datetime import timedelta

@login_required
def client_bikes(request):
    bikes = Bike.objects.filter(user=request.user)
    return render(request, "client/bike_list.html", {
        "bikes": bikes
    })


@login_required
def client_bike_history(request, bike_id):
    bike = get_object_or_404(Bike, id=bike_id, user=request.user)

    services = ServiceRequest.objects.filter(
        bike=bike
    ).order_by("-created_at")

    next_service_date = None
    if services.exists():
        next_service_date = services.first().created_at + timedelta(days=90)

    return render(request, "client/bike_history.html", {
        "bike": bike,
        "services": services,
        "next_service_date": next_service_date
    })

@login_required
def submit_feedback(request, service_id):
    from .models import Feedback
    service = get_object_or_404(ServiceRequest, id=service_id, user=request.user, status='completed')
    
    # Block if already reviewed
    if hasattr(service, 'feedback'):
        return redirect('client_dashboard')

    if request.method == 'POST':
        rating = int(request.POST.get('rating', 5))
        comment = request.POST.get('comment', '')
        
        Feedback.objects.create(
            service_request=service,
            rating=rating,
            comment=comment,
            is_public=True
        )
        return redirect('client_dashboard')

    return render(request, 'client/submit_feedback.html', {'service': service})

