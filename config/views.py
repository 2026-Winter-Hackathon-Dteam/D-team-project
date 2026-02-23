from django.http import HttpResponse
from django.db import connection

def health_check(request):
    try:
        connection.ensure_connection()
        return HttpResponse("OK", status=200)
    except Exception:
        return HttpResponse("DB Error", status=500)