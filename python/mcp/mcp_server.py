from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
# Set up OpenTelemetry

trace.set_tracer_provider(TracerProvider())
trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))


from amazon.opentelemetry.distro.patches._starlette_patches import _apply_starlette_instrumentation_patches
_apply_starlette_instrumentation_patches()

from amazon.opentelemetry.distro.patches._fastmcp_patches import _apply_fastmcp_instrumentation_patches
_apply_fastmcp_instrumentation_patches()

from opentelemetry.instrumentation.starlette import StarletteInstrumentor

StarletteInstrumentor().instrument()


from mcp.server.fastmcp import FastMCP
from starlette.responses import JSONResponse
mcp = FastMCP(host="0.0.0.0", stateless_http=True)

@mcp.tool()
def add_numbers(a: int, b: int) -> int:
    """Add two numbers together"""
    return a + b

@mcp.tool()
def multiply_numbers(a: int, b: int) -> int:
    """Multiply two numbers together"""
    return a * b

@mcp.tool()
def greet_user(name: str) -> str:
    """Greet a user by name"""
    return f"Hello, {name}! Nice to meet you."

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
