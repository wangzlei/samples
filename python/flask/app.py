#!/usr/bin/env python3
"""
Simple Flask application sample.

This is a basic Flask app that demonstrates:
- Basic routing
- JSON responses
- Template rendering
- Static file serving

To run:
    pip install flask
    python app.py

The app will be available at http://localhost:5000
"""
import sys

import requests

sys.setrecursionlimit(5000)

from flask import Flask, jsonify, render_template_string

app = Flask(__name__)

# Simple HTML template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Simple Flask App</title>
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
        <h1>Simple Flask Application</h1>
        <p>Welcome to this basic Flask app!</p>

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
            <h3><a href="/hello/World">/hello/&lt;name&gt;</a></h3>
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


@app.route("/")
def home():
    """Home page with links to all endpoints."""
    return render_template_string(HTML_TEMPLATE)


@app.route("/hello")
def hello():
    _demo_client()

    _demo_otel_span_decorator()

    _demo_otel_span_api1()

    _demo_otel_span_api2()

    """Simple hello endpoint."""
    return '<h1>Hello, Flask!</h1><p><a href="/">← Back to home</a></p>'


def _demo_client():
    """A demo function to illustrate recursion limit increase."""

    requests.get("https://aws.amazon.com/")


from opentelemetry import trace

# Creates a tracer from the global tracer provider
tracer = trace.get_tracer("my.tracer.name")


@tracer.start_as_current_span("create-otel-span-by-decorator")
def _demo_otel_span_decorator():
    pass


def _demo_otel_span_api1():
    """A demo function to illustrate OpenTelemetry span context manager."""
    with tracer.start_as_current_span("create-otel-span-by-api"):

        requests.get("https://aws.amazon.com/")

        pass


def _demo_otel_span_api2():
    span = tracer.start_span("create-otel-span-by-api-2")
    span.end()


@app.route("/hello/<name>")
def hello_name(name):
    """Personalized hello endpoint."""
    return f'<h1>Hello, {name}!</h1><p><a href="/">← Back to home</a></p>'


@app.route("/api/status")
def api_status():
    """JSON status endpoint."""
    return jsonify({"status": "ok", "message": "Flask app is running", "version": "1.0.0"})


@app.route("/api/info")
def api_info():
    """Application information endpoint."""
    return jsonify(
        {
            "app_name": "Simple Flask App",
            "description": "A basic Flask application sample",
            "endpoints": [
                {"path": "/", "method": "GET", "description": "Home page"},
                {"path": "/hello", "method": "GET", "description": "Simple hello"},
                {"path": "/hello/<name>", "method": "GET", "description": "Personalized hello"},
                {"path": "/api/status", "method": "GET", "description": "Status check"},
                {"path": "/api/info", "method": "GET", "description": "App information"},
            ],
        }
    )


if __name__ == "__main__":
    print("Starting Simple Flask App...")
    print("Visit http://localhost:8000 to see the app")
    app.run(debug=True, host="0.0.0.0", port=8000)
