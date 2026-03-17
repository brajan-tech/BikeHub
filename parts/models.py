from django.db import models

class SparePart(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    stock_quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.name} ({self.stock_quantity})"


class ServicePartUsage(models.Model):
    service_request = models.ForeignKey(
        "core.ServiceRequest",
        on_delete=models.CASCADE,
        related_name="part_usages"
    )

    spare_part = models.ForeignKey(
        SparePart,
        on_delete=models.CASCADE
    )

    quantity_used = models.PositiveIntegerField()

    price_per_piece = models.DecimalField(
    max_digits=10,
    decimal_places=2,
    default=0
    )


    total_price = models.IntegerField(default=0)

    def __str__(self):
        return (
            f"{self.service_request.bike.bike_number} | "
            f"{self.spare_part.name} | "
            f"Qty: {self.quantity_used}"
            )



