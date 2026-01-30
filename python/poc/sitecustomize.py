"""
OpenTelemetry Managed Environment Injection Script

This script is automatically loaded by Python at startup and patches the OpenTelemetry SDK
to inject managed monitoring capabilities without requiring user code changes.

Place this file in a directory that's at the front of PYTHONPATH (e.g., /opt/managed/python).
"""

import sys
import os
import importlib.util
import logging

# Configure logging for debugging injection process
logging.basicConfig(
    level=logging.INFO,
    format='[%(name)s] %(levelname)s: %(message)s'
)
logger = logging.getLogger("ManagedInformer")

# Environment variable to disable managed injection if needed
MANAGED_OTEL_DISABLED = os.environ.get("MANAGED_OTEL_DISABLED", "false").lower() == "true"

# Global flag to track if lazy injection has been done
_LAZY_INJECTION_DONE = False

# Global dict to track which TracerProvider instances已经添加了我们的 processor
_MANAGED_PROCESSOR_ADDED = {}


def apply_managed_patch():
    """
    Patch OpenTelemetry TracerProvider to automatically inject managed monitoring.
    
    This function uses multiple strategies:
    1. Patch TracerProvider.__init__ 
    2. Patch TracerProvider.add_span_processor (for zero-code scenarios)
    3. Handles errors gracefully to avoid breaking user applications
    """
    if MANAGED_OTEL_DISABLED:
        logger.info("Managed OpenTelemetry injection is disabled via MANAGED_OTEL_DISABLED.")
        return
    
    try:
        # Dynamic import to avoid crashes if OpenTelemetry is not installed
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        from my_managed_lib import MyCustomExporter
        
        # Strategy 1: Patch __init__
        original_init = TracerProvider.__init__
        
        def patched_init(self, *args, **kwargs):
            """Patched TracerProvider.__init__ that adds managed monitoring."""
            logger.info("TracerProvider.__init__ called!")
            original_init(self, *args, **kwargs)
            
            try:
                logger.info("About to add managed processor in __init__...")
                managed_exporter = MyCustomExporter()
                managed_processor = BatchSpanProcessor(managed_exporter)
                self.add_span_processor(managed_processor)
                logger.info("Successfully added managed SpanProcessor in __init__.")
            except Exception as e:
                logger.error(f"Failed to add managed processor in __init__: {e}", exc_info=True)
        
        TracerProvider.__init__ = patched_init
        logger.info("TracerProvider.__init__ patched successfully.")
        
        # Note: We don't patch add_span_processor for Scenario B
        # The __init__ patch is sufficient for manual initialization
        
    except ImportError as e:
        logger.debug(f"OpenTelemetry SDK not found, skipping patch: {e}")
    except Exception as e:
        logger.error(f"Unexpected error during patching: {e}", exc_info=True)


def patch_set_tracer_provider():
    """
    Note: For Scenario B, we don't patch set_tracer_provider
    The __init__ patch is sufficient for manual initialization
    """
    pass


def chain_load_sitecustomize():
    """
    Chain-load other sitecustomize.py files to ensure compatibility
    with tools like opentelemetry-instrument.
    
    This allows multiple sitecustomize.py files to coexist by loading
    them in sequence from sys.path.
    
    IMPORTANT: We load ALL sitecustomize.py files, not just the first one.
    """
    current_file = os.path.abspath(__file__)
    loaded_files = []
    
    for path in sys.path:
        if not path:
            continue
        
        target = os.path.abspath(os.path.join(path, "sitecustomize.py"))
        
        # Skip if it's this file or doesn't exist or already loaded
        if not os.path.exists(target) or target == current_file or target in loaded_files:
            continue
        
        try:
            # Dynamically load and execute the sitecustomize.py
            spec = importlib.util.spec_from_file_location(f"sitecustomize_{len(loaded_files)}", target)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            loaded_files.append(target)
            logger.info(f"Chain-loaded sitecustomize from: {target}")
        except Exception as e:
            logger.error(f"Error chain-loading sitecustomize from {target}: {e}")
    
    if loaded_files:
        logger.info(f"Total chain-loaded {len(loaded_files)} sitecustomize.py files")


def setup_lazy_injection():
    """
    Setup lazy injection that triggers when user code first accesses tracing.
    This solves the timing issue where TracerProvider is created after sitecustomize
    but before user code runs.
    """
    global _LAZY_INJECTION_DONE
    
    if MANAGED_OTEL_DISABLED:
        return
    
    try:
        from opentelemetry import trace
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        from my_managed_lib import MyCustomExporter
        
        # Backup original get_tracer
        original_get_tracer = trace.get_tracer
        
        def lazy_injecting_get_tracer(*args, **kwargs):
            """Wrapped get_tracer that injects on first call."""
            global _LAZY_INJECTION_DONE
            
            # Only inject once
            if not _LAZY_INJECTION_DONE:
                _LAZY_INJECTION_DONE = True
                try:
                    provider = trace.get_tracer_provider()
                    logger.info(f"🎯 Lazy injection triggered! Provider: {type(provider).__name__}")
                    
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
                            logger.info("✅ Successfully injected managed processor via lazy injection!")
                        else:
                            logger.info("Managed processor already present.")
                except Exception as e:
                    logger.error(f"Error during lazy injection: {e}", exc_info=True)
            
            # Call original get_tracer
            return original_get_tracer(*args, **kwargs)
        
        # Apply the wrapper
        trace.get_tracer = lazy_injecting_get_tracer
        logger.info("Lazy injection setup complete.")
        
    except Exception as e:
        logger.error(f"Error setting up lazy injection: {e}", exc_info=True)


def inject_into_existing_provider():
    """
    Immediate injection attempt (for sitecustomize stage).
    This is kept for backward compatibility but lazy injection is more reliable.
    """
    if MANAGED_OTEL_DISABLED:
        return
    
    try:
        from opentelemetry import trace
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        from my_managed_lib import MyCustomExporter
        
        # Get the current global tracer provider
        provider = trace.get_tracer_provider()
        logger.info(f"Checking existing provider: {type(provider).__name__}")
        
        # Check if it's an SDK TracerProvider (not the default no-op one)
        if isinstance(provider, TracerProvider):
            # Check if we haven't already added our processor
            processors = provider._active_span_processor._span_processors
            logger.info(f"Found {len(processors)} existing processors")
            
            # Check if MyCustomExporter is already in the processors
            has_managed = any(
                hasattr(p, 'span_exporter') and 
                type(p.span_exporter).__name__ == 'MyCustomExporter'
                for p in processors
            )
            
            if not has_managed:
                logger.info("MyCustomExporter not found, injecting now...")
                managed_exporter = MyCustomExporter()
                managed_processor = BatchSpanProcessor(managed_exporter)
                provider.add_span_processor(managed_processor)
                logger.info("Successfully injected managed processor into existing TracerProvider!")
            else:
                logger.info("Managed processor already present in TracerProvider.")
        else:
            logger.info(f"Provider is not TracerProvider: {type(provider).__name__}")
                
    except Exception as e:
        logger.error(f"Error injecting into existing provider: {e}", exc_info=True)


def patch_auto_instrumentation_initialize():
    """
    Patch opentelemetry.instrumentation.auto_instrumentation.initialize to inject our processor.
    This is called by opentelemetry-instrument's sitecustomize.
    """
    if MANAGED_OTEL_DISABLED:
        return
    
    try:
        from opentelemetry.instrumentation import auto_instrumentation
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        from my_managed_lib import MyCustomExporter
        
        original_initialize = auto_instrumentation.initialize
        
        def patched_initialize():
            """Patched initialize that adds our processor after initialization."""
            logger.info("🎯 auto_instrumentation.initialize called!")
            
            # Call original initialize
            result = original_initialize()
            
            # Now inject our managed processor
            try:
                from opentelemetry import trace
                provider = trace.get_tracer_provider()
                
                logger.info(f"Provider after initialize: {type(provider).__name__}")
                
                if isinstance(provider, TracerProvider):
                    processors = provider._active_span_processor._span_processors
                    logger.info(f"Found {len(processors)} existing processors")
                    
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
                        logger.info("✅ Successfully injected managed processor via initialize patch!")
                    else:
                        logger.info("Managed processor already present.")
                else:
                    logger.warning(f"Provider is not TracerProvider: {type(provider)}")
            except Exception as e:
                logger.error(f"Failed to inject via initialize: {e}", exc_info=True)
            
            return result
        
        auto_instrumentation.initialize = patched_initialize
        logger.info("auto_instrumentation.initialize patched successfully.")
        
    except ImportError as e:
        logger.debug(f"auto_instrumentation module not found: {e}")
    except Exception as e:
        logger.error(f"Error patching initialize: {e}", exc_info=True)


# Main execution flow
if __name__ != "__main__":
    # This is executed when Python imports this module automatically
    logger.info("Managed OpenTelemetry sitecustomize.py loaded.")
    
    # Step 1: Patch TracerProvider class (only once!)
    apply_managed_patch()
    
    # Step 2: Patch set_tracer_provider function (additional safety)
    patch_set_tracer_provider()
    
    # Step 3: Patch auto_instrumentation.initialize (for opentelemetry-instrument scenario)
    patch_auto_instrumentation_initialize()
    
    # Step 4: Chain-load other sitecustomize.py files (e.g., from opentelemetry-instrument)
    chain_load_sitecustomize()
    
    # Step 5: Setup lazy injection AFTER chain-load
    # This must be done AFTER chain-load to ensure we patch the correct trace module
    setup_lazy_injection()
    
    # Step 6: Inject into any existing provider (immediate fallback)
    inject_into_existing_provider()
    
    logger.info("Managed OpenTelemetry injection complete.")
