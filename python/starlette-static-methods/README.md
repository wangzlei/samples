# Starlette Static Methods Sample

This sample demonstrates how to use static methods as route handlers in a Starlette application, utilizing the route registration method (`app.add_route()`) instead of declaring routes in the constructor.

## Features Demonstrated

- **Static Methods as Route Handlers**: All endpoints are handled by static methods from different classes
- **Route Registration Method**: Uses `app.add_route()` to register routes programmatically
- **Class-based Organization**: Handlers are organized in logical classes (ApiHandlers, UserHandlers, MathHandlers)
- **Multiple HTTP Methods**: Demonstrates GET and POST methods
- **Path Parameters**: Shows how to handle path parameters in static method handlers
- **Error Handling**: Includes proper error responses with status codes
- **JSON and HTML Responses**: Mixed response types from static methods

## Key Differences from Regular Route Definition

Instead of defining routes in the Starlette constructor like this:
```python
routes = [
    Route("/", homepage),
    Route("/users", get_users),
]
app = Starlette(routes=routes)
```

This sample uses the route registration method:
```python
app = Starlette()
app.add_route("/", ApiHandlers.home, methods=["GET"])
app.add_route("/users", UserHandlers.list_users, methods=["GET"])
```

## Static Method Handler Examples

### Basic Static Method Handler
```python
class ApiHandlers:
    @staticmethod
    async def get_status(request):
        return JSONResponse({"status": "healthy"})
```

### Static Method with Path Parameters
```python
class UserHandlers:
    @staticmethod
    async def get_user(request):
        user_id = request.path_params["user_id"]
        # Handle the request...
```

### Static Method with Error Handling
```python
class MathHandlers:
    @staticmethod
    async def add_numbers(request):
        try:
            a = int(request.path_params["a"])
            b = int(request.path_params["b"])
            return JSONResponse({"result": a + b})
        except ValueError:
            return JSONResponse(
                {"error": "Invalid numbers"}, 
                status_code=400
            )
```

## Available Endpoints

- `GET /` - Home page with endpoint documentation
- `GET /api/status` - System status check
- `GET /api/info` - Application information
- `GET /users` - List all users
- `POST /users` - Create a new user
- `GET /users/{user_id}` - Get specific user by ID
- `GET /math/add/{a}/{b}` - Add two numbers
- `GET /math/multiply/{a}/{b}` - Multiply two numbers

## Running the Sample

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:
   ```bash
   python app.py
   ```

3. Visit http://localhost:8000 to see the application

## Benefits of This Approach

1. **Clean Organization**: Static methods keep handlers organized in logical classes
2. **No Instance State**: Static methods don't require class instances, making them lightweight
3. **Flexible Route Registration**: Routes can be registered conditionally or dynamically
4. **Easy Testing**: Static methods are easy to test independently
5. **Clear Separation**: Different handler classes can handle different aspects of the API

## Use Cases

This pattern is particularly useful for:
- Large applications with many endpoints
- API endpoints that don't need shared state
- Modular applications where routes are added conditionally
- Clean separation of concerns between different API domains
