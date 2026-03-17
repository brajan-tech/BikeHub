from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from io import BytesIO

def calculate_parts_total(service_request):
    # ✅ import INSIDE function (this breaks circular import)
    from parts.models import ServicePartUsage

    total = 0

    usages = ServicePartUsage.objects.filter(
        service_request=service_request
    )

    for u in usages:
        total += u.quantity_used * u.price_per_piece

    return total


def render_to_pdf(template_src, context_dict):
    template = get_template(template_src)
    html = template.render(context_dict)

    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)

    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type="application/pdf")
    return None
