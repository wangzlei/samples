"""
Replacement sitecustomize.py for opentelemetry-instrument with managed monitoring injection.

This file should replace the original sitecustomize.py in:
/path/to/venv/lib/python3.x/site-packages/opentelemetry/instrumentation/auto_instrumentation/sitecustomize.py

Usage:
  cp sitecustomize_replacement.py /path/to/venv/lib/python3.x/site-packages/opentelemetry/instrumentation/auto_instrumentation/sitecustomize.py
"""

from opentelemetry.instrumentation.auto_instrumentation import initialize
import logging

logger = logging.getLogger("ManagedInformer")
logging.basicConfig(level=logging.INFO, format='[%(name)s] %(levelname)s: %(message)s')

def inject_managed_monitoring():
    """Inject managed monitoring processor after OpenTelemetry initialization."""
    try:
        from opentelemetry import trace
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        
        # Import the managed exporter
        # NOTE: This assumes my_managed_lib is available in PYTHONPATH
        import sys
        import os
        # Add the managed lib directory to path if needed
        managed_lib_dir = os.environ.get('MANAGED_LIB_PATH', '/opt/managed/python')
        if managed_lib_dir not in sys.path:
            sys.path.insert(0, managed_lib_dir)
        
        from my_managed_lib import MyCustomExporter
        
        provider = trace.get_tracer_provider()
        logger.info(f"🎯 Injecting managed monitoring. Provider: {type(provider).__name__}")
        
        if isinstance(provider, TracerProvider):
            processors = provider._active_span_processor._span_processors
            
            # Check if MyCustomExporter is already present
            has_managed = any(
                hasattr(p, 'span_exporter') and 
                type(p.span_exporter).__name__ == 'MyCustomExporter'
                for p in processors
            )
            
            if not has_managed:
                managed_exporter = MyCustomExporter()
                managed_processor = BatchSpanProcessor(managed_exporter)
                provider.add_span_processor(managed_processor)
                logger.info("✅ Successfully injected managed processor!")
                logger.info(f"Total processors: {len(provider._active_span_processor._span_processors)}")
            else:
                logger.info("Managed processor already present.")
        else:
            logger.warning(f"Provider is not TracerProvider: {type(provider)}")
            
    except Exception as e:
        logger.error(f"Failed to inject managed monitoring: {e}", exc_info=True)

# First, initialize OpenTelemetry as normal
logger.info("Initializing OpenTelemetry with managed monitoring...")
initialize()

# Then, inject our managed monitoring
inject_managed_monitoring()

logger.info("OpenTelemetry initialization complete with managed monitoring.")
