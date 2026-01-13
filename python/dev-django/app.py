"""
Django views for the dev-django sample application.
"""
from django.http import HttpResponse

def hello_world(request):
    """Simple hello world view."""
    return HttpResponse("Hello World!!")
