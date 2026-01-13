# Simple Flask Application Sample

This is a basic Flask application that demonstrates core Flask functionality without any OpenTelemetry instrumentation.

## Features

- Basic routing with multiple endpoints
- JSON API responses
- HTML template rendering
- Static content serving
- Clean, simple code structure

## Endpoints

- `GET /` - Home page with links to all endpoints
- `GET /hello` - Simple hello message
- `GET /hello/<name>` - Personalized hello message
- `GET /api/status` - JSON status response
- `GET /api/info` - Application information in JSON format

## Requirements

- Python 3.7+
- Flask 3.0.0

## Installation & Usage

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:
   ```bash
   python app.py
   ```

3. Open your browser and visit:
   ```
   http://localhost:5000
   ```

## Example API Responses

### Status endpoint (`/api/status`):
```json
{
  "status": "ok",
  "message": "Flask app is running",
  "version": "1.0.0"
}
```

### Info endpoint (`/api/info`):
```json
{
  "app_name": "Simple Flask App",
  "description": "A basic Flask application sample",
  "endpoints": [
    {"path": "/", "method": "GET", "description": "Home page"},
    {"path": "/hello", "method": "GET", "description": "Simple hello"},
    {"path": "/hello/<name>", "method": "GET", "description": "Personalized hello"},
    {"path": "/api/status", "method": "GET", "description": "Status check"},
    {"path": "/api/info", "method": "GET", "description": "App information"}
  ]
}
```

## Development

The application runs in debug mode by default, which enables:
- Auto-reload on code changes
- Detailed error pages
- Debug toolbar (if installed)

To run in production mode, modify the `app.run()` call in `app.py`:
```python
app.run(debug=False, host='0.0.0.0', port=5000)
```

## Notes

This is a minimal Flask application intended for demonstration purposes. It includes no authentication, database connections, or advanced features - just the basic Flask functionality to get you started.
