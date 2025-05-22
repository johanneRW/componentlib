from django.http import HttpResponse

def htmx_view(func):
    func._is_htmx_view = True
    return func

@htmx_view
def htmx_dropdown_response(request):
    val = request.GET.get("dropdown", "")
    return HttpResponse(f"<p>Du valgte: <strong>{val}</strong></p>")
