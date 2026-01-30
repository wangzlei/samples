"""
Test Scenario B: Manual Initialization with Explicit TracerProvider Setup

This script demonstrates the managed injection working with manual TracerProvider initialization.

Usage:
    PYTHONPATH=/path/to/poc:$PYTHONPATH python test_scenario_b_manual.py

Expected behavior:
    - sitecustomize.py loads at Python startup and patches TracerProvider class
    - User code manually creates and configures TracerProvider with Console Exporter
    - Managed SpanProcessor is automatically added during __init__
    - Both Console and ManagedExporter output spans (parallel working!)
"""

import time
import logging
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, BatchSpanProcessor
from opentelemetry.sdk.resources import Resource

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Test with user-configured console exporter + managed exporter."""
    
    logger.info("="*70)
    logger.info("Scenario B: Manual Initialization Test")
    logger.info("="*70)
    logger.info("")
    
    # Create TracerProvider with custom configuration
    resource = Resource.create({
        "service.name": "scenario-b-manual-service",
        "service.version": "1.0.0",
    })
    
    provider = TracerProvider(resource=resource)
    
    # User adds their own console exporter
    logger.info("User: Adding Console Exporter...")
    console_exporter = ConsoleSpanExporter()
    console_processor = BatchSpanProcessor(console_exporter)
    provider.add_span_processor(console_processor)
    
    # Set as global provider
    trace.set_tracer_provider(provider)
    
    logger.info("TracerProvider setup complete")
    logger.info(f"Total processors: {len(provider._active_span_processor._span_processors)}")
    logger.info("")
    
    # Get tracer
    tracer = trace.get_tracer(__name__)
    
    # Create one test span
    logger.info("Creating a test span...")
    logger.info("")
    with tracer.start_as_current_span("test_operation") as span:
        span.set_attribute("operation.type", "manual_test")
        span.set_attribute("test.scenario", "B")
        span.add_event("processing_started")
        time.sleep(0.1)
        span.add_event("processing_completed")
    
    # Force flush to see output
    provider.force_flush()
    time.sleep(1)
    
    logger.info("\n" + "="*70)
    logger.info("✅ Test Complete!")
    logger.info("="*70)
    logger.info("\nYou should see:")
    logger.info("  1. '[ManagedInformer]' logs showing injection success")
    logger.info("  2. Total processors: 2 (console + managed)")
    logger.info("  3. Console span output (JSON format from user's exporter)")
    logger.info("  4. '[ManagedExporter]' logs with detailed span information")
    logger.info("\n✨ Both exporters working in parallel!")


if __name__ == "__main__":
    main()
