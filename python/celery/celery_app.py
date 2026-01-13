#!/usr/bin/env python3
"""
Celery application configuration.

This module sets up the Celery application instance with Redis as the broker.
"""

from celery import Celery

# Create Celery instance
app = Celery("celery_sample")

# Configuration
app.config_from_object(
    {
        "broker_url": "redis://localhost:6379/0",
        "result_backend": "redis://localhost:6379/0",
        "task_serializer": "json",
        "result_serializer": "json",
        "accept_content": ["json"],
        "result_expires": 3600,
        "timezone": "UTC",
        "enable_utc": True,
        "include": ["tasks"],  # Include task modules
    }
)

if __name__ == "__main__":
    app.start()
