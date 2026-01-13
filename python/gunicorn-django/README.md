# Gunicorn Django Sample

A simple Django application with a "Hello World" endpoint, configured to run with Gunicorn WSGI server using traditional Django project structure.

## Features

- Traditional Django project structure with separate files
- Simple hello world endpoint at `/` and `/hello/`
- Gunicorn WSGI server configuration
- OpenTelemetry instrumentation ready
- Uses `DJANGO_SETTINGS_MODULE` environment variable

## Project Structure

```
samples/gunicorn-django/
├── app.py              # Django views
├── settings.py         # Django settings
├── urls.py             # URL configuration
├── wsgi.py             # WSGI application
├── gunicorn.conf.py    # Gunicorn configuration
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Django Settings Module

**For DJANGO_SETTINGS_MODULE, point to:** `settings`

```bash
export DJANGO_SETTINGS_MODULE=settings
```

## Running the Application

### Standard Gunicorn (Recommended)
```bash
export DJANGO_SETTINGS_MODULE=settings
gunicorn -c gunicorn.conf.py wsgi:application
```

### With command line options
```bash
export DJANGO_SETTINGS_MODULE=settings
gunicorn --bind 0.0.0.0:8000 --workers 2 wsgi:application
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

To run with OpenTelemetry instrumentation:

```bash
# Auto-instrumentation
opentelemetry-instrument gunicorn -c gunicorn.conf.py app:application

# With AWS OpenTelemetry Distro
opentelemetry-instrument --distro=aws_distro gunicorn -c gunicorn.conf.py app:application
```

## Configuration

- **Port**: 8000 (configurable in `gunicorn.conf.py`)
- **Workers**: 2 (configurable in `gunicorn.conf.py`)
- **Worker Class**: sync
- **Timeout**: 30 seconds
