#!/usr/bin/env python3
"""
Starlette application with static methods sample.

This demonstrates:
- Using static methods as route handlers
- Route registration using add_route method
- Class-based organization of handlers
- Various HTTP methods with static methods
- JSON and HTML responses from static methods

To run:
    pip install -r requirements.txt
    python app.py

The app will be available at http://localhost:8000
"""

import requests
import uvicorn
from starlette.applications import Starlette
from starlette.responses import HTMLResponse, JSONResponse

# HTML template for home page
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Starlette Static Methods Sample</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .container { max-width: 600px; margin: 0 auto; }
        .endpoint { margin: 20px 0; padding: 10px; background: #f5f5f5; border-radius: 5px; }
        a { color: #007bff; text-decoration: none; }
        a:hover { text-decoration: underline; }
        .method { color: #28a745; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Starlette Static Methods Application</h1>
        <p>This sample demonstrates using static methods as route handlers with route registration.</p>

        <h2>Available Endpoints:</h2>

        <div class="endpoint">
            <h3><a href="/">GET /</a></h3>
            <p>Home page (static method handler)</p>
        </div>

        <div class="endpoint">
            <h3><a href="/api/status">GET /api/status</a></h3>
            <p>System status (static method handler)</p>
        </div>

        <div class="endpoint">
            <h3><a href="/api/info">GET /api/info</a></h3>
            <p>Application info (static method handler)</p>
        </div>

        <div class="endpoint">
            <h3><a href="/users">GET /users</a></h3>
            <p>List users (static method handler)</p>
        </div>

        <div class="endpoint">
            <h3><span class="method">POST</span> /users</h3>
            <p>Create user (static method handler)</p>
        </div>

        <div class="endpoint">
            <h3><a href="/users/123">GET /users/{user_id}</a></h3>
            <p>Get specific user (static method handler)</p>
        </div>

        <div class="endpoint">
            <h3><a href="/math/add/5/3">GET /math/add/{a}/{b}</a></h3>
            <p>Mathematical operations (static utility methods)</p>
        </div>
    </div>
</body>
</html>
"""


class ApiHandlers:
    """Class containing static method handlers for API endpoints."""

    @staticmethod
    async def home(request):
        """Home page handler using static method."""
        return HTMLResponse(HTML_TEMPLATE)

    @staticmethod
    async def get_status(request):
        """Status endpoint handler using static method."""
        # Make a request to demonstrate instrumentation
        requests.get("https://httpbin.org/status/200")
        
        return JSONResponse({
            "status": "healthy",
            "message": "Starlette app with static methods is running",
            "version": "1.0.0",
            "handler_type": "static_method"
        })

    @staticmethod
    async def get_info(request):
        """Info endpoint handler using static method."""
        return JSONResponse({
            "app_name": "Starlette Static Methods Sample",
            "description": "Demonstrates using static methods as route handlers",
            "framework": "Starlette",
            "features": [
                "Static method route handlers",
                "Route registration with add_route",
                "Class-based handler organization",
                "Async static methods",
                "Multiple HTTP methods"
            ],
            "handler_type": "static_method"
        })


class UserHandlers:
    """Class containing static method handlers for user-related endpoints."""

    # Simulated user database
    users_db = {
        "123": {"id": "123", "name": "John Doe", "email": "john@example.com"},
        "456": {"id": "456", "name": "Jane Smith", "email": "jane@example.com"}
    }

    @staticmethod
    async def list_users(request):
        """List all users using static method."""
        return JSONResponse({
            "users": list(UserHandlers.users_db.values()),
            "count": len(UserHandlers.users_db),
            "handler_type": "static_method"
        })

    @staticmethod
    async def create_user(request):
        """Create a new user using static method."""
        # In a real app, you'd parse request body
        new_user = {
            "id": "789",
            "name": "New User",
            "email": "newuser@example.com",
            "created": "via_static_method"
        }
        
        UserHandlers.users_db["789"] = new_user
        
        return JSONResponse({
            "message": "User created successfully",
            "user": new_user,
            "handler_type": "static_method"
        }, status_code=201)

    @staticmethod
    async def get_user(request):
        """Get specific user using static method."""
        user_id = request.path_params["user_id"]
        
        if user_id in UserHandlers.users_db:
            return JSONResponse({
                "user": UserHandlers.users_db[user_id],
                "handler_type": "static_method"
            })
        else:
            return JSONResponse({
                "error": "User not found",
                "user_id": user_id,
                "handler_type": "static_method"
            }, status_code=404)


class MathHandlers:
    """Class containing static method handlers for mathematical operations."""

    @staticmethod
    async def add_numbers(request):
        """Add two numbers using static method."""
        try:
            a = int(request.path_params["a"])
            b = int(request.path_params["b"])
            result = a + b
            
            return JSONResponse({
                "operation": "addition",
                "a": a,
                "b": b,
                "result": result,
                "formula": f"{a} + {b} = {result}",
                "handler_type": "static_method"
            })
        except ValueError:
            return JSONResponse({
                "error": "Invalid numbers provided",
                "handler_type": "static_method"
            }, status_code=400)

    @staticmethod
    async def multiply_numbers(request):
        """Multiply two numbers using static method."""
        try:
            a = int(request.path_params["a"])
            b = int(request.path_params["b"])
            result = a * b
            
            return JSONResponse({
                "operation": "multiplication",
                "a": a,
                "b": b,
                "result": result,
                "formula": f"{a} × {b} = {result}",
                "handler_type": "static_method"
            })
        except ValueError:
            return JSONResponse({
                "error": "Invalid numbers provided",
                "handler_type": "static_method"
            }, status_code=400)


# Create the Starlette application
app = Starlette()

# Register routes using add_route method with static methods
# This demonstrates the route registration method approach

# API routes
app.add_route("/", ApiHandlers.home, methods=["GET"])
app.add_route("/api/status", ApiHandlers.get_status, methods=["GET"])
app.add_route("/api/info", ApiHandlers.get_info, methods=["GET"])

# User routes
app.add_route("/users", UserHandlers.list_users, methods=["GET"])
app.add_route("/users", UserHandlers.create_user, methods=["POST"])
app.add_route("/users/{user_id}", UserHandlers.get_user, methods=["GET"])

# Math routes
app.add_route("/math/add/{a}/{b}", MathHandlers.add_numbers, methods=["GET"])
app.add_route("/math/multiply/{a}/{b}", MathHandlers.multiply_numbers, methods=["GET"])


if __name__ == "__main__":
    print("Starting Starlette Static Methods Sample App...")
    print("This sample demonstrates:")
    print("- Static methods as route handlers")
    print("- Route registration using app.add_route() method")
    print("- Class-based organization of handlers")
    print("")
    print("Visit http://localhost:8000 to see the app")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
