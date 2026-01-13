# Dev Django Sample

A simple Django application with a "Hello World" endpoint, configured to run with Django's built-in development server using `python manage.py runserver`.

## Features

- Simplified Django project structure with embedded settings
- Simple hello world endpoint at `/` and `/hello/`
- Django built-in development server
- OpenTelemetry instrumentation ready
- No separate settings.py file - settings embedded in manage.py

## Project Structure

```
samples/dev-django/
├── app.py              # Django views
├── urls.py             # URL configuration
├── manage.py           # Django management script with embedded settings
├── wsgi.py             # WSGI application for production deployment
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

### Standard Django Development Server (Recommended)
```bash
python manage.py runserver
```

### With specific port and host
```bash
python manage.py runserver 0.0.0.0:8000
```

### With different port
```bash
python manage.py runserver 8001
```

## Running with WSGI Server (Production)

### Using Gunicorn
```bash
# Basic usage
gunicorn wsgi:application

# With specific port and workers
gunicorn --bind 0.0.0.0:8000 --workers 2 wsgi:application

# With reload (development)
gunicorn --bind 0.0.0.0:8000 --workers 2 --reload wsgi:application
```

### Using other WSGI servers
```bash
# With uWSGI
uwsgi --http :8000 --module wsgi:application

# With Waitress
waitress-serve --host=0.0.0.0 --port=8000 wsgi:application
```

## Testing

Once the server is running, you can test the endpoints:

```bash
# Test root endpoint
curl http://localhost:8000/

# Test explicit hello endpoint
curl http://localhost:8000/hello/
```

Both should return: `Hello World!`

## OpenTelemetry Instrumentation

### With Development Server
```bash
# Auto-instrumentation
opentelemetry-instrument python manage.py runserver

# With AWS OpenTelemetry Distro
opentelemetry-instrument --distro=aws_distro python manage.py runserver
```

### With WSGI Server (Gunicorn)
```bash
# Auto-instrumentation with Gunicorn
opentelemetry-instrument gunicorn wsgi:application

# With AWS OpenTelemetry Distro
opentelemetry-instrument --distro=aws_distro gunicorn --bind 0.0.0.0:8000 --workers 2 wsgi:application
```

## Configuration

- **Port**: 8000 (default for Django development server)
- **Workers**: Single-threaded development server
- **Auto-reload**: Enabled by default (development feature)
- **Debug**: Enabled (development setting)

## Differences from gunicorn-django

This sample is designed for development use with Django's built-in server, while the `gunicorn-django` sample is designed for production deployment:

- Uses `python manage.py runserver` instead of `gunicorn`
- No `wsgi.py` or `gunicorn.conf.py` files needed
- Includes `manage.py` for Django management commands
- Single-threaded development server with auto-reload
- Optimized for development workflow
