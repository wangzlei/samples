#!/usr/bin/env python3
"""
Celery tasks definition.

This module defines various Celery tasks for demonstration purposes.
"""

import random
import time

from celery_app import app


@app.task
def add_numbers(x, y):
    """Simple task that adds two numbers."""
    return x + y


@app.task
def multiply_numbers(x, y):
    """Simple task that multiplies two numbers."""
    return x * y


@app.task
def long_running_task(duration=10):
    """
    A long-running task that simulates work.

    Args:
        duration: How long the task should run (in seconds)

    Returns:
        dict: Status information about the completed task
    """
    for i in range(duration):
        time.sleep(1)
        # Update task state to show progress
        app.current_task.update_state(
            state="PROGRESS",
            meta={"current": i + 1, "total": duration, "status": f"Processing step {i + 1}/{duration}"},
        )

    return {"status": "Task completed successfully!", "duration": duration, "result": f"Processed {duration} steps"}


@app.task
def generate_random_data(count=100):
    """
    Generate random data points.

    Args:
        count: Number of random data points to generate

    Returns:
        list: List of random numbers
    """
    return [random.randint(1, 1000) for _ in range(count)]


@app.task
def process_data(data):
    """
    Process a list of data (calculate statistics).

    Args:
        data: List of numbers to process

    Returns:
        dict: Statistics about the data
    """
    if not data:
        return {"error": "No data provided"}

    return {"count": len(data), "sum": sum(data), "average": sum(data) / len(data), "min": min(data), "max": max(data)}


@app.task
def chain_example(x):
    """
    Example task for chaining.
    Squares the input and adds 10.
    """
    result = x * x + 10
    time.sleep(2)  # Simulate some work
    return result


@app.task(bind=True, autoretry_for=(Exception,), retry_kwargs={"max_retries": 3})
def failing_task(self, fail_probability=0.7):
    """
    A task that randomly fails to demonstrate retry behavior.

    Args:
        fail_probability: Probability of failure (0.0 to 1.0)
    """
    if random.random() < fail_probability:
        raise Exception(f"Task failed randomly (attempt {self.request.retries + 1})")

    return {
        "status": "success",
        "attempts": self.request.retries + 1,
        "message": "Task completed successfully after some retries!",
    }
