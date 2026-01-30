"""
Custom Managed Exporter for OpenTelemetry

This module provides a custom SpanExporter that can be used by managed environments
to export telemetry data to their own backend systems.
"""

import logging
from typing import Sequence
from opentelemetry.sdk.trace.export import SpanExporter, SpanExportResult
from opentelemetry.sdk.trace import ReadableSpan

# Configure logger to ensure messages are visible
logger = logging.getLogger("ManagedExporter")
logger.setLevel(logging.INFO)

# Only add handler if none exists AND parent doesn't have handlers
if not logger.handlers and not logger.parent.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('[%(name)s] %(levelname)s: %(message)s'))
    logger.addHandler(handler)


class MyCustomExporter(SpanExporter):
    """
    Custom SpanExporter for managed environments.
    
    This exporter can be configured to send telemetry data to:
    - Internal monitoring systems
    - Cloud-specific backends (AWS X-Ray, Azure Monitor, Google Cloud Trace)
    - Custom aggregation pipelines
    - Multi-backend destinations
    
    In production, replace the implementation with actual export logic.
    """
    
    def __init__(self, endpoint: str = None, service_name: str = None):
        """
        Initialize the custom exporter.
        
        Args:
            endpoint: Optional backend endpoint URL
            service_name: Optional service name for grouping spans
        """
        self.endpoint = endpoint or "https://managed-backend.example.com/traces"
        self.service_name = service_name or "managed-service"
        logger.info(f"MyCustomExporter initialized with endpoint: {self.endpoint}")
    
    def export(self, spans: Sequence[ReadableSpan]) -> SpanExportResult:
        """
        Export spans to the managed backend.
        
        Args:
            spans: Sequence of spans to export
            
        Returns:
            SpanExportResult indicating success or failure
        """
        try:
            # Log spans for demonstration purposes
            logger.info(f"Exporting {len(spans)} spans to managed backend")
            
            for span in spans:
                # Extract key span information
                span_data = {
                    "trace_id": format(span.context.trace_id, "032x"),
                    "span_id": format(span.context.span_id, "016x"),
                    "name": span.name,
                    "start_time": span.start_time,
                    "end_time": span.end_time,
                    "duration_ns": span.end_time - span.start_time if span.end_time else None,
                    "attributes": dict(span.attributes) if span.attributes else {},
                    "status": span.status.status_code.name if span.status else "UNSET",
                    "service_name": self.service_name,
                }
                
                # Log detailed span information
                duration_ms = span_data['duration_ns'] / 1_000_000 if span_data['duration_ns'] else 0
                
                logger.info(f"  → Span: {span.name}")
                logger.info(f"      TraceID: {span_data['trace_id']}")
                logger.info(f"      SpanID:  {span_data['span_id']}")
                logger.info(f"      Status:  {span_data['status']}")
                logger.info(f"      Duration: {duration_ms:.2f}ms")
                
                # Log attributes if present
                if span_data['attributes']:
                    logger.info(f"      Attributes: {span_data['attributes']}")
                
                # Log parent span if present
                if span.parent:
                    parent_span_id = format(span.parent.span_id, "016x")
                    logger.info(f"      Parent: {parent_span_id}")
                
                # Log events if present
                if span.events:
                    logger.info(f"      Events: {len(span.events)} event(s)")
                    for event in span.events[:3]:  # Show first 3 events
                        logger.info(f"        - {event.name}")
                
                # TODO: Replace with actual backend export logic
                # Examples:
                # - HTTP POST to monitoring endpoint
                # - Write to message queue (Kafka, SQS, RabbitMQ)
                # - Send to cloud-native backend (X-Ray, Cloud Trace, etc.)
                # - Store in database or data lake
                
                # Example HTTP export (commented out):
                # import requests
                # response = requests.post(
                #     self.endpoint,
                #     json=span_data,
                #     headers={"Content-Type": "application/json"},
                #     timeout=5
                # )
                # response.raise_for_status()
            
            logger.info(f"Successfully exported {len(spans)} spans")
            return SpanExportResult.SUCCESS
            
        except Exception as e:
            # Defensive: never crash user application due to export failure
            logger.error(f"Failed to export spans: {e}", exc_info=True)
            return SpanExportResult.FAILURE
    
    def shutdown(self) -> None:
        """
        Shutdown the exporter and release resources.
        """
        logger.info("MyCustomExporter shutting down")
        # TODO: Cleanup any resources (connections, file handles, etc.)
    
    def force_flush(self, timeout_millis: int = 30000) -> bool:
        """
        Force flush any pending spans.
        
        Args:
            timeout_millis: Maximum time to wait for flush in milliseconds
            
        Returns:
            True if flush succeeded, False otherwise
        """
        logger.info("Force flush requested")
        # TODO: Implement actual flush logic if buffering spans
        return True


class MultiBackendExporter(SpanExporter):
    """
    Example exporter that sends spans to multiple backends simultaneously.
    
    Useful for:
    - Sending to both managed backend and user's own monitoring
    - A/B testing different backends
    - Gradual migration scenarios
    """
    
    def __init__(self, exporters: list[SpanExporter]):
        """
        Initialize with multiple exporters.
        
        Args:
            exporters: List of SpanExporter instances
        """
        self.exporters = exporters
        logger.info(f"MultiBackendExporter initialized with {len(exporters)} exporters")
    
    def export(self, spans: Sequence[ReadableSpan]) -> SpanExportResult:
        """
        Export spans to all configured backends.
        
        Returns SUCCESS only if all exporters succeed.
        """
        results = []
        for exporter in self.exporters:
            try:
                result = exporter.export(spans)
                results.append(result)
            except Exception as e:
                logger.error(f"Exporter {exporter.__class__.__name__} failed: {e}")
                results.append(SpanExportResult.FAILURE)
        
        # Return SUCCESS only if all succeeded
        if all(r == SpanExportResult.SUCCESS for r in results):
            return SpanExportResult.SUCCESS
        else:
            return SpanExportResult.FAILURE
    
    def shutdown(self) -> None:
        """Shutdown all exporters."""
        for exporter in self.exporters:
            try:
                exporter.shutdown()
            except Exception as e:
                logger.error(f"Error shutting down exporter: {e}")
    
    def force_flush(self, timeout_millis: int = 30000) -> bool:
        """Force flush all exporters."""
        return all(
            exporter.force_flush(timeout_millis)
            for exporter in self.exporters
        )
