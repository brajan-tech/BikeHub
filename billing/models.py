from django.db import models


class Invoice(models.Model):
    service_request = models.OneToOneField(
        "core.ServiceRequest",
        on_delete=models.CASCADE
    )

    labour_charge = models.IntegerField(default=0)
    parts_total = models.IntegerField(default=0)
    grand_total = models.IntegerField(default=0)


    created_at = models.DateTimeField(auto_now_add=True)

    def calculate_totals(self):
        parts_sum = sum(part.total_price for part in self.parts.all())
        self.parts_total = parts_sum
        self.grand_total = self.labour_charge + parts_sum
        self.save()

    def __str__(self):
        return f"Invoice #{self.id}"


class InvoicePart(models.Model):
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name="parts"
    )

    part_name = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField(default=1)
    price_per_piece = models.DecimalField(max_digits=8, decimal_places=2)

    @property
    def total_price(self):
        return self.quantity * self.price_per_piece

    def __str__(self):
        return f"{self.part_name} ({self.quantity})"
