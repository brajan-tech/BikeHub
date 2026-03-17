from django.contrib import admin
from .models import WorkProgress

@admin.register(WorkProgress)
class WorkProgressAdmin(admin.ModelAdmin):

    autocomplete_fields = ("service_request",)

    list_display = (
        "service_request",
        "get_mechanic",
        "status",
    )

    search_fields = (
        "service_request__bike__registration_number",
        "service_request__bike__model_name",
        "service_request__mechanic__user__username",
        "status",
    )

    def get_mechanic(self, obj):
        if obj.service_request and obj.service_request.mechanic:
            return obj.service_request.mechanic.user.username
        return "-"
    get_mechanic.short_description = "Mechanic"
