import os
import sys

from amazon.opentelemetry.distro.code_correlation.code_attributes_span_processor import CodeAttributesSpanProcessor
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")


import django

django.setup()


# Set up OpenTelemetry
code_attributes_processor = CodeAttributesSpanProcessor()

trace.set_tracer_provider(TracerProvider())
trace.get_tracer_provider().add_span_processor(code_attributes_processor)
trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))


from amazon.opentelemetry.distro.patches._django_patches import _apply_django_instrumentation_patches

_apply_django_instrumentation_patches()


from opentelemetry.instrumentation.django import DjangoInstrumentor

DjangoInstrumentor().instrument()

from opentelemetry.instrumentation.requests import RequestsInstrumentor

RequestsInstrumentor().instrument()

from opentelemetry.instrumentation.botocore import BotocoreInstrumentor

BotocoreInstrumentor().instrument()

# Enable SQLite database instrumentation to generate database client spans
from opentelemetry.instrumentation.sqlite3 import SQLite3Instrumentor

SQLite3Instrumentor().instrument()


from django.core.management import call_command

port = "8000"
if len(sys.argv) > 1:
    port = sys.argv[1]

call_command("runserver", f"127.0.0.1:{port}")
