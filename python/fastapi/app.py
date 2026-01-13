#!/usr/bin/env python3
"""
Simple FastAPI application sample.

This is a basic FastAPI app that demonstrates:
- Basic routing
- JSON responses
- Path parameters
- Async endpoints
- Automatic OpenAPI documentation

To run:
    pip install -r requirements.txt
    python app.py

The app will be available at http://localhost:8000
OpenAPI docs will be available at http://localhost:8000/docs
"""

import boto3
import uvicorn
from botocore.exceptions import ClientError, NoCredentialsError
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI(title="Simple FastAPI App", description="A basic FastAPI application sample", version="1.0.0")

# Simple HTML template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Simple FastAPI App</title>
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
        <h1>Simple FastAPI Application</h1>
        <p>Welcome to this basic FastAPI app!</p>

        <h2>Available Endpoints:</h2>

        <div class="endpoint">
            <h3><a href="/">/</a></h3>
            <p>This home page</p>
        </div>

        <div class="endpoint">
            <h3><a href="/hello">/hello</a></h3>
            <p>Simple hello message with S3 bucket listing</p>
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

        <div class="endpoint">
            <h3><a href="/docs">/docs</a></h3>
            <p>Interactive API documentation (Swagger UI)</p>
        </div>

        <div class="endpoint">
            <h3><a href="/redoc">/redoc</a></h3>
            <p>Alternative API documentation (ReDoc)</p>
        </div>
    </div>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
async def home():
    """Home page with links to all endpoints."""
    import requests

    requests.get("https://aws.amazon.com/")
    return HTML_TEMPLATE


@app.get("/hello")
async def hello():
    """Simple hello endpoint with S3 bucket listing."""
    response = {"message": "Hello, FastAPI!", "link": {"home": "/"}}

    try:
        s3 = boto3.client("s3")
        buckets = s3.list_buckets()
        bucket_names = [bucket["Name"] for bucket in buckets.get("Buckets", [])]
        response["s3_buckets"] = bucket_names
    except NoCredentialsError:
        response["s3_buckets"] = "No AWS credentials found."

    return response


@app.get("/hello/{name}")
async def hello_name(name: str):
    """Personalized hello endpoint."""
    return {"message": f"Hello, {name}!", "name": name, "link": {"home": "/"}}


@app.get("/api/status")
async def api_status():
    """JSON status endpoint."""
    return {"status": "ok", "message": "FastAPI app is running", "version": "1.0.0", "framework": "FastAPI"}


@app.get("/api/info")
async def api_info():
    """Application information endpoint."""
    return {
        "app_name": "Simple FastAPI App",
        "description": "A basic FastAPI application sample",
        "framework": "FastAPI",
        "python_async": True,
        "automatic_docs": True,
        "endpoints": [
            {"path": "/", "method": "GET", "description": "Home page"},
            {"path": "/hello", "method": "GET", "description": "Simple hello with S3 bucket listing"},
            {"path": "/hello/{name}", "method": "GET", "description": "Personalized hello"},
            {"path": "/api/status", "method": "GET", "description": "Status check"},
            {"path": "/api/info", "method": "GET", "description": "App information"},
            {"path": "/docs", "method": "GET", "description": "Interactive API docs"},
            {"path": "/redoc", "method": "GET", "description": "Alternative API docs"},
        ],
        "features": [
            "Async/await support",
            "Automatic OpenAPI/Swagger documentation",
            "Type hints and validation",
            "High performance",
        ],
    }


if __name__ == "__main__":
    print("Starting Simple FastAPI App...")
    print("Visit http://localhost:8000 to see the app")
    print("Visit http://localhost:8000/docs for interactive API documentation")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
