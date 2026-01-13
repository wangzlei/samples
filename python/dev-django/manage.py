#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import django
from django.conf import settings
from django.core.management import execute_from_command_line

# Initialize OpenTelemetry tracer
from opentelemetry import trace
from opentelemetry.sdk.trace.export import ConsoleSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.semconv.resource import ResourceAttributes
from opentelemetry.instrumentation.django import DjangoInstrumentor

# Configure resource with service information
resource = Resource.create({
    ResourceAttributes.SERVICE_NAME: "dev-django-sample",
    ResourceAttributes.SERVICE_VERSION: "1.0.0",
    ResourceAttributes.DEPLOYMENT_ENVIRONMENT: "development"
})

# Set up tracer provider only if not already configured
if not hasattr(trace.get_tracer_provider(), '_real_tracer_provider'):
    trace.set_tracer_provider(TracerProvider(resource=resource))
    tracer_provider = trace.get_tracer_provider()

    # Configure console span exporter
    console_exporter = ConsoleSpanExporter()

    # Add span processor
    span_processor = BatchSpanProcessor(console_exporter)
    tracer_provider.add_span_processor(span_processor)

# # Enable Django instrumentation after Django is set up
# DjangoInstrumentor().instrument()

def main():
    """Run administrative tasks."""
    # Configure Django settings directly in code
    if not settings.configured:
        settings.configure(
            DEBUG=True,
            SECRET_KEY='dev-secret-key-not-for-production',
            ALLOWED_HOSTS=['127.0.0.1', 'localhost', '*'],
            MIDDLEWARE=[
                'django.middleware.security.SecurityMiddleware',
                'django.middleware.common.CommonMiddleware',
            ],
            INSTALLED_APPS=[
                'django.contrib.contenttypes',
                'django.contrib.auth',
            ],
            DATABASES={
                'default': {
                    'ENGINE': 'django.db.backends.sqlite3',
                    'NAME': ':memory:',
                }
            },
            ROOT_URLCONF='urls',
        )
        django.setup()
        
        # Enable Django instrumentation after Django is set up
        DjangoInstrumentor().instrument()
    
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
