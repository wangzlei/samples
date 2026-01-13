import views
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from views import TestViewSet, ProductViewSet, HealthViewSet

# DRF Router registration (similar to pet clinic insurance service)
router = DefaultRouter()
router.register(r'api/test', TestViewSet, basename='test')
router.register(r'api/products', ProductViewSet, basename='products')
router.register(r'api/health', HealthViewSet, basename='health')

urlpatterns = [
    # Original function-based and class-based views
    path("", views.hello, name="hello"),  # Root path
    path("hello/", views.hello, name="hello_explicit"),  # Explicit /hello/ path
    path("test/", views.test_view, name="test"),
    path("slow/", views.slow_view, name="slow"),
    path("param/<int:param_id>/", views.parameterized_view, name="parameterized"),
    path("class/", views.TestClassView.as_view(), name="class_view"),
    path("template/", views.TestTemplateView.as_view(), name="template_view"),
    path("error/", views.error_view, name="error_view"),
    path("debug/", views.debug_middleware_view, name="debug_middleware"),
    path("orm/", views.orm_example_view, name="orm_example"),
    
    # DRF ViewSet routes (similar to pet clinic insurance service pattern)
    path('', include(router.urls)),
    # Alternative namespace pattern (commented for reference)
    # path('api/', include((router.urls, 'service'), namespace='service')),
]
