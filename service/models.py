from django.db import models

class WorkProgress(models.Model):
    service_request = models.ForeignKey(
        'core.ServiceRequest',
        on_delete=models.CASCADE,
        related_name='progress_updates'
    )

    status = models.CharField(max_length=50)
    note = models.TextField(blank=True)
    photo = models.ImageField(upload_to='work_photos/', blank=True, null=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.service_request} - {self.status}"
