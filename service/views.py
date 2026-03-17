from django.shortcuts import render
from core.models import Bike, ServiceRequest

def bike_history(request):
    history = None
    bike = None

    reg_no = request.POST.get("reg_no") or request.GET.get("reg_no")

    if reg_no:
        bike = Bike.objects.filter(bike_number__iexact=reg_no).first()

        if bike:
            history = []
            services = ServiceRequest.objects.filter(
                bike=bike
            ).select_related("mechanic").order_by("-created_at")

            for s in services:
                if hasattr(s, "problem") and s.problem:
                    problem_text = s.problem
                elif hasattr(s, "description") and s.problem:
                    problem_text = s.problem
                else:
                    problem_text = "Not mentioned"

                history.append({
                    "date": s.created_at,
                    "problem": problem_text,
                    "mechanic": s.mechanic,
                    "parts": s.servicepartusage_set.all(),
                })

    return render(request, "service/bike_history.html", {
        "bike": bike,
        "history": history
    })

    return render(request, "service/bike_history.html", {
        "bike": bike,
        "history": history,
        "error": error,
    })
