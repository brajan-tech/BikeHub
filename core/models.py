from django.db import models
from django.contrib.auth.models import User
from mechanics.models import Mechanic
from billing.models import Invoice
from billing.utils import calculate_parts_total
from django.utils import timezone
# =========================
# Bike Model
# =========================
class Bike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bike_name = models.CharField(max_length=100)
    bike_number = models.CharField(max_length=20)
    photo = models.ImageField(upload_to='bike_photos/', null=True, blank=True)


    def __str__(self):
        return f"{self.bike_name} ({self.bike_number})"


# =========================
# Service Request Model
# =========================
class EmailNotification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=255)
    message = models.TextField()

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("sent", "Sent"),
        ("failed", "Failed"),
    ]
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="pending"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.user.username} - {self.subject}"

class ServiceRequest(models.Model):
    bike = models.ForeignKey("core.Bike", on_delete=models.CASCADE)
    status = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.bike.registration_number} - {self.status}"


    # -------------------------
    # STATUS
    # -------------------------
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    completed_at = models.DateTimeField(null=True, blank=True)

    # -------------------------
    # RELATIONS
    # -------------------------
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bike = models.ForeignKey(Bike, on_delete=models.CASCADE)

    mechanic = models.ForeignKey(
        Mechanic,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    # -------------------------
    # DETAILS
    # -------------------------
    problem_description = models.TextField(blank=True)

    labour_charge = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=500.00
    )

    work_photo = models.ImageField(
        upload_to='work_photos/',
        null=True,
        blank=True
    )

    # -------------------------
    # TIMESTAMPS
    # -------------------------
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # -------------------------
    # METHODS
    # -------------------------
    def mark_completed(self):
        if self.status == 'completed':
            return
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save()


    def __str__(self):
        return f"{self.bike} - {self.status}"

    # =========================
    # AUTO INVOICE CREATION
    # =========================
    def save(self, *args, **kwargs):
        creating = self.pk is None
        old_status = None

        if not creating:
            old_status = ServiceRequest.objects.get(pk=self.pk).status

        super().save(*args, **kwargs)

        # Create invoice ONLY when status changes to completed
        if self.status == 'completed' and old_status != 'completed':
            if not Invoice.objects.filter(service_request=self).exists():
                parts_total = calculate_parts_total(self)
                labour = self.labour_charge

                Invoice.objects.create(
                    service_request=self,
                    labour_charge=labour,
                    parts_total=parts_total,
                    grand_total=labour + parts_total
                )

# =========================
# FEEDBACK
# =========================
class Feedback(models.Model):
    service_request = models.OneToOneField(ServiceRequest, on_delete=models.CASCADE, related_name='feedback')
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    comment = models.TextField()
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback for {self.service_request} - {self.rating}/5"

# =========================
# ENQUIRY
# =========================
class Enquiry(models.Model):
    name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    message = models.TextField(verbose_name="What Enquiry")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Enquiry from {self.name} ({self.phone_number})"

