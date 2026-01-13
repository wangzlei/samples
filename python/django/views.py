import json
import os
import time
from datetime import datetime, timedelta

import boto3
import requests
from django.http import HttpResponse, JsonResponse
from django.views import View
from django.views.generic import TemplateView
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Count, Avg, Max, Subquery, OuterRef
from django.core.paginator import Paginator

# Import removed - using Django built-in models instead

s3 = boto3.client("s3")
dynamodb = boto3.resource("dynamodb")


def hello(request):
    """Simple function-based view"""
    requests.get("https://aws.amazon.com/")
    return HttpResponse("Hello, Django!")


def test_view(request):
    """Test view to check if process_view is called"""
    requests.get("https://aws.amazon.com/")
    return JsonResponse({"message": "Test view called successfully", "method": request.method, "path": request.path})


def slow_view(request):
    """View that takes some time to process"""
    time.sleep(0.5)  # Simulate some processing
    return JsonResponse({"message": "Slow view completed", "processing_time": "0.5 seconds"})


def parameterized_view(request, param_id):
    """View with URL parameters"""
    return JsonResponse({"message": f"Parameterized view called with ID: {param_id}", "param_id": param_id})


class TestClassView(View):
    """Class-based view"""

    def get(self, request):
        return JsonResponse({"message": "Class-based GET view", "view_type": "class-based"})

    def post(self, request):
        return JsonResponse({"message": "Class-based POST view", "view_type": "class-based", "method": "POST"})


class TestTemplateView(TemplateView):
    """Template-based view"""

    def get(self, request, *args, **kwargs):

        self._internal()

        return JsonResponse({"message": "Template-based view", "view_type": "template-based"})

    def _internal(self):

        requests.get("https://aws.amazon.com/")

        s3.list_buckets()

        list(dynamodb.tables.all())

        pid = os.getpid()
        output = os.popen(f"ps -o pid,rss,command -p {pid}").read()
        print(output)


def error_view(request):
    """View that raises an exception"""
    raise ValueError("This is a test exception for tracing")


def debug_middleware_view(request):
    """View to debug middleware execution"""
    requests.get("https://aws.amazon.com/")
    return JsonResponse(
        {
            "message": "Debug middleware view",
            "request_meta_keys": list(request.META.keys())[:10],  # First 10 keys
            "has_otel_keys": {
                "activation_key": "opentelemetry-instrumentor-django.activation_key" in request.META,
                "span_key": "opentelemetry-instrumentor-django.span_key" in request.META,
            },
        }
    )


# Django REST Framework ViewSets
class TestViewSet(viewsets.ViewSet):
    """Test ViewSet for DRF routing"""
    
    def list(self, request):
        """GET /test/"""
        requests.get("https://aws.amazon.com/")
        return Response({
            "message": "Test ViewSet list action",
            "method": "GET",
            "action": "list"
        })
    
    def create(self, request):
        """POST /test/"""
        requests.get("https://aws.amazon.com/")
        return Response({
            "message": "Test ViewSet create action",
            "method": "POST",
            "action": "create",
            "data": request.data
        }, status=status.HTTP_201_CREATED)
    
    def retrieve(self, request, pk=None):
        """GET /test/{id}/"""
        requests.get("https://aws.amazon.com/")
        return Response({
            "message": f"Test ViewSet retrieve action for ID: {pk}",
            "method": "GET",
            "action": "retrieve",
            "pk": pk
        })
    
    def update(self, request, pk=None):
        """PUT /test/{id}/"""
        requests.get("https://aws.amazon.com/")
        return Response({
            "message": f"Test ViewSet update action for ID: {pk}",
            "method": "PUT",
            "action": "update",
            "pk": pk,
            "data": request.data
        })
    
    def destroy(self, request, pk=None):
        """DELETE /test/{id}/"""
        requests.get("https://aws.amazon.com/")
        return Response({
            "message": f"Test ViewSet destroy action for ID: {pk}",
            "method": "DELETE",
            "action": "destroy",
            "pk": pk
        }, status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=False, methods=['get'])
    def custom_action(self, request):
        """GET /test/custom_action/"""
        requests.get("https://aws.amazon.com/")
        return Response({
            "message": "Custom action on TestViewSet",
            "method": "GET",
            "action": "custom_action"
        })


class ProductViewSet(viewsets.ViewSet):
    """Product ViewSet for testing DRF routing"""
    
    def list(self, request):
        """GET /products/"""
        requests.get("https://aws.amazon.com/")
        s3.list_buckets()
        return Response({
            "message": "Product ViewSet list action",
            "products": [
                {"id": 1, "name": "Product 1", "price": 10.99},
                {"id": 2, "name": "Product 2", "price": 20.99}
            ]
        })
    
    def create(self, request):
        """POST /products/"""
        requests.get("https://aws.amazon.com/")
        return Response({
            "message": "Product ViewSet create action",
            "created_product": {
                "id": 3,
                "name": request.data.get("name", "New Product"),
                "price": request.data.get("price", 0.0)
            }
        }, status=status.HTTP_201_CREATED)
    
    def retrieve(self, request, pk=None):
        """GET /products/{id}/"""
        requests.get("https://aws.amazon.com/")
        return Response({
            "message": f"Product ViewSet retrieve action for ID: {pk}",
            "product": {
                "id": pk,
                "name": f"Product {pk}",
                "price": 15.99
            }
        })
    
    @action(detail=True, methods=['post'])
    def purchase(self, request, pk=None):
        """POST /products/{id}/purchase/"""
        requests.get("https://aws.amazon.com/")
        time.sleep(0.2)  # Simulate processing
        return Response({
            "message": f"Purchase action for product ID: {pk}",
            "product_id": pk,
            "quantity": request.data.get("quantity", 1),
            "total": float(request.data.get("quantity", 1)) * 15.99
        })


class HealthViewSet(viewsets.ViewSet):
    """Health ViewSet for monitoring"""
    
    def list(self, request):
        """GET /health/"""
        return Response({
            "status": "healthy",
            "timestamp": time.time(),
            "service": "Django DRF Sample"
        })
    
    @action(detail=False, methods=['get'])
    def status(self, request):
        """GET /health/status/"""
        requests.get("https://aws.amazon.com/")
        return Response({
            "application": "Django DRF Sample",
            "status": "running",
            "database": "connected",
            "external_api": "reachable"
        })
    
    @action(detail=False, methods=['get'])
    def detailed(self, request):
        """GET /health/detailed/"""
        requests.get("https://aws.amazon.com/")
        s3.list_buckets()
        list(dynamodb.tables.all())
        
        return Response({
            "application": "Django DRF Sample",
            "status": "running",
            "checks": {
                "database": "healthy",
                "s3": "healthy",
                "dynamodb": "healthy",
                "external_api": "healthy"
            },
            "timestamp": time.time()
        })


# Simple ORM example demonstrating code attributes behavior
def orm_example_view(request):
    """
    Simple view demonstrating Django ORM code attributes behavior
    
    This mimics the pattern from pet_clinic_billing_service/views.py:56
    where objs = list(qs) generates a client span with code attributes 
    pointing to CursorDebugWrapper._execute instead of this user code.
    
    Uses Django's built-in User model to avoid needing custom migrations.
    """
    from django.contrib.auth.models import User
    
    # Create a queryset using built-in User model (similar to billing service pattern)
    qs = User.objects.filter(is_active=True)[:10]
    
    # This line forces QuerySet evaluation and generates a database CLIENT span
    # Code attributes will point to: 
    #   code.function.name: "django.db.backends.utils.CursorDebugWrapper._execute"
    #   code.file.path: "/usr/local/lib/python3.10/site-packages/django/db/backends/utils.py"  
    # NOT to this line in views.py
    objs = list(qs)  # <- This is the equivalent of the billing service line 56
    
    return JsonResponse({
        "message": "ORM example completed",
        "users_found": len(objs),
        "note": "Check spans - code attributes point to Django internal code, not this view"
    })
