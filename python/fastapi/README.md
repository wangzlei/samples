# Simple FastAPI Application Sample

This is a basic FastAPI application that demonstrates core FastAPI functionality without any OpenTelemetry instrumentation.

## Features

- Async/await support for high performance
- Automatic OpenAPI (Swagger) documentation
- Type hints and automatic validation
- Path parameters and JSON responses
- Multiple endpoint types
- Clean, modern async code structure

## Endpoints

- `GET /` - Home page with links to all endpoints
- `GET /hello` - Simple hello message
- `GET /hello/{name}` - Personalized hello message with path parameter
- `GET /api/status` - JSON status response
- `GET /api/info` - Application information in JSON format
- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /redoc` - Alternative API documentation (ReDoc)

## Requirements

- Python 3.7+
- FastAPI 0.104.1
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

4. Explore the automatic API documentation:
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## Example API Responses

### Status endpoint (`/api/status`):
```json
{
  "status": "ok",
  "message": "FastAPI app is running",
  "version": "1.0.0",
  "framework": "FastAPI"
}
```

### Info endpoint (`/api/info`):
```json
{
  "app_name": "Simple FastAPI App",
  "description": "A basic FastAPI application sample",
  "framework": "FastAPI",
  "python_async": true,
  "automatic_docs": true,
  "endpoints": [
    {"path": "/", "method": "GET", "description": "Home page"},
    {"path": "/hello", "method": "GET", "description": "Simple hello"},
    {"path": "/hello/{name}", "method": "GET", "description": "Personalized hello"},
    {"path": "/api/status", "method": "GET", "description": "Status check"},
    {"path": "/api/info", "method": "GET", "description": "App information"},
    {"path": "/docs", "method": "GET", "description": "Interactive API docs"},
    {"path": "/redoc", "method": "GET", "description": "Alternative API docs"}
  ],
  "features": [
    "Async/await support",
    "Automatic OpenAPI/Swagger documentation",
    "Type hints and validation",
    "High performance"
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

## FastAPI Features Demonstrated

1. **Async/Await**: All endpoints use async functions for better performance
2. **Type Hints**: Path parameters use Python type hints for automatic validation
3. **Automatic Documentation**: FastAPI generates OpenAPI docs automatically
4. **Response Models**: Different response types (HTML, JSON)
5. **Path Parameters**: Dynamic URL segments with type validation
6. **Modern Python**: Uses current Python async/await syntax

## Notes

This is a minimal FastAPI application intended for demonstration purposes. It includes no authentication, database connections, or advanced features - just the basic FastAPI functionality to get you started. The automatic API documentation at `/docs` and `/redoc` is one of FastAPI's standout features that makes it easy to explore and test your API.
