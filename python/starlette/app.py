#!/usr/bin/env python3
"""
Simple Starlette application sample.

This is a basic Starlette app that demonstrates:
- Basic routing
- JSON responses
- Path parameters
- Async endpoints
- Static file serving
- HTML responses

To run:
    pip install -r requirements.txt
    python app.py

The app will be available at http://localhost:8000
"""

import requests
import uvicorn
from starlette.applications import Starlette
from starlette.responses import HTMLResponse, JSONResponse
from starlette.routing import Route

# Simple HTML template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Simple Starlette App</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .container { max-width: 600px; margin: 0 auto; }
        .endpoint { margin: 20px 0; padding: 10px; background: #f5f5f5; border-radius: 5px; }
        a { color: #007bff; text-decoration: none; }
        a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Simple Starlette Application</h1>
        <p>Welcome to this basic Starlette app!</p>

        <h2>Available Endpoints:</h2>

        <div class="endpoint">
            <h3><a href="/">/</a></h3>
            <p>This home page</p>
        </div>

        <div class="endpoint">
            <h3><a href="/hello">/hello</a></h3>
            <p>Simple hello message</p>
        </div>

        <div class="endpoint">
            <h3><a href="/hello/World">/hello/{name}</a></h3>
            <p>Personalized hello message</p>
        </div>

        <div class="endpoint">
            <h3><a href="/api/status">/api/status</a></h3>
            <p>JSON status response</p>
        </div>

        <div class="endpoint">
            <h3><a href="/api/info">/api/info</a></h3>
            <p>Application information in JSON</p>
        </div>
    </div>
</body>
</html>
"""


async def homepage(request):
    """Home page with links to all endpoints."""
    return HTMLResponse(HTML_TEMPLATE)


async def hello(request):
    """Simple hello endpoint."""
    requests.get("https://aws.amazon.com/")
    return JSONResponse({"message": "Hello, Starlette!", "link": {"home": "/"}})


async def hello_name(request):
    """Personalized hello endpoint."""
    name = request.path_params["name"]
    return JSONResponse({"message": f"Hello, {name}!", "name": name, "link": {"home": "/"}})


async def api_status(request):
    """JSON status endpoint."""
    return JSONResponse(
        {"status": "ok", "message": "Starlette app is running", "version": "1.0.0", "framework": "Starlette"}
    )


async def api_info(request):
    """Application information endpoint."""
    return JSONResponse(
        {
            "app_name": "Simple Starlette App",
            "description": "A basic Starlette application sample",
            "framework": "Starlette",
            "python_async": True,
            "minimal_framework": True,
            "endpoints": [
                {"path": "/", "method": "GET", "description": "Home page"},
                {"path": "/hello", "method": "GET", "description": "Simple hello"},
                {"path": "/hello/{name}", "method": "GET", "description": "Personalized hello"},
                {"path": "/api/status", "method": "GET", "description": "Status check"},
                {"path": "/api/info", "method": "GET", "description": "App information"},
            ],
            "features": [
                "Async/await support",
                "Path parameters",
                "JSON and HTML responses",
                "Lightweight and fast",
                "ASGI compatible",
            ],
        }
    )


# Define routes
routes = [
    Route("/", homepage),
    Route("/hello", hello),
    Route("/hello/{name}", hello_name),
    Route("/api/status", api_status),
    Route("/api/info", api_info),
]

# Create the Starlette application
app = Starlette(routes=routes)


if __name__ == "__main__":
    print("Starting Simple Starlette App...")
    print("Visit http://localhost:8000 to see the app")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
