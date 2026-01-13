# Simple Starlette Application Sample

This is a basic Starlette application that demonstrates core Starlette functionality without any OpenTelemetry instrumentation.

## Features

- Async/await support for high performance
- Lightweight ASGI framework
- Path parameters and JSON responses
- HTML responses with templates
- Multiple endpoint types
- Clean, modern async code structure
- Minimal dependencies

## Endpoints

- `GET /` - Home page with links to all endpoints
- `GET /hello` - Simple hello message
- `GET /hello/{name}` - Personalized hello message with path parameter
- `GET /api/status` - JSON status response
- `GET /api/info` - Application information in JSON format

## Requirements

- Python 3.7+
- Starlette 0.27.0
- Uvicorn 0.24.0 (ASGI server)

## Installation & Usage

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:
   ```bash
   python app.py
   ```

   Or alternatively using uvicorn directly:
   ```bash
   uvicorn app:app --host 0.0.0.0 --port 8000 --reload
   ```

3. Open your browser and visit:
   ```
   http://localhost:8000
   ```

## Example API Responses

### Status endpoint (`/api/status`):
```json
{
  "status": "ok",
  "message": "Starlette app is running",
  "version": "1.0.0",
  "framework": "Starlette"
}
```

### Info endpoint (`/api/info`):
```json
{
  "app_name": "Simple Starlette App",
  "description": "A basic Starlette application sample",
  "framework": "Starlette",
  "python_async": true,
  "minimal_framework": true,
  "endpoints": [
    {"path": "/", "method": "GET", "description": "Home page"},
    {"path": "/hello", "method": "GET", "description": "Simple hello"},
    {"path": "/hello/{name}", "method": "GET", "description": "Personalized hello"},
    {"path": "/api/status", "method": "GET", "description": "Status check"},
    {"path": "/api/info", "method": "GET", "description": "App information"}
  ],
  "features": [
    "Async/await support",
    "Path parameters",
    "JSON and HTML responses",
    "Lightweight and fast",
    "ASGI compatible"
  ]
}
```

### Hello with name (`/hello/World`):
```json
{
  "message": "Hello, World!",
  "name": "World",
  "link": {"home": "/"}
}
```

## Development

The application runs with automatic reload enabled by default when using the `python app.py` command, which enables:
- Auto-reload on code changes
- Detailed error messages
- Interactive debugging

For production deployment, you would typically use:
```bash
uvicorn app:app --host 0.0.0.0 --port 8000
```

## Starlette Features Demonstrated

1. **Async/Await**: All endpoints use async functions for better performance
2. **Path Parameters**: Dynamic URL segments accessible via `request.path_params`
3. **Response Types**: Different response types (HTMLResponse, JSONResponse)
4. **Route Definition**: Clean route definition using the Route class
5. **ASGI Application**: Modern Python web application using ASGI
6. **Lightweight**: Minimal framework with just the essentials

## Notes

This is a minimal Starlette application intended for demonstration purposes. Starlette is a lightweight ASGI framework that provides the foundation for FastAPI and other frameworks. It includes no authentication, database connections, or advanced features - just the basic Starlette functionality to get you started.

Unlike FastAPI, Starlette does not include automatic API documentation generation, but it provides the core building blocks for high-performance async web applications with minimal overhead.

## Starlette vs FastAPI

This sample demonstrates pure Starlette, which is:
- More lightweight than FastAPI
- Requires manual request/response handling
- Does not include automatic API documentation
- Provides more direct control over the application
- Serves as the foundation that FastAPI is built upon

If you need automatic API documentation, type validation, and other high-level features, consider using FastAPI instead, which builds on top of Starlette.
