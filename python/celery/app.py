#!/usr/bin/env python3
"""
Flask application that demonstrates Celery task execution.

This Flask app provides a web interface to trigger and monitor Celery tasks.
It demonstrates various Celery features including:
- Basic task execution
- Long-running tasks with progress tracking
- Task chaining
- Error handling and retries

To run:
    1. Start Redis: docker-compose up -d redis
    2. Start Celery worker: celery -A celery_app worker --loglevel=info
    3. Start Flask app: python app.py
    4. Visit http://localhost:5000
"""

import json

from celery import chain, chord, group
from celery_app import app as celery_app
from flask import Flask, jsonify, render_template_string, request
from tasks import (
    add_numbers,
    chain_example,
    failing_task,
    generate_random_data,
    long_running_task,
    multiply_numbers,
    process_data,
)

app = Flask(__name__)

# HTML template for the web interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Celery Sample App</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .container { max-width: 800px; margin: 0 auto; }
        .task-section { margin: 30px 0; padding: 20px; background: #f8f9fa; border-radius: 8px; }
        .task-section h3 { margin-top: 0; color: #2c3e50; }
        button { 
            background: #007bff; color: white; border: none; padding: 10px 20px; 
            border-radius: 4px; cursor: pointer; margin: 5px; 
        }
        button:hover { background: #0056b3; }
        .result { 
            margin: 10px 0; padding: 10px; background: #e9ecef; 
            border-radius: 4px; font-family: monospace; 
        }
        input[type="number"] { 
            padding: 8px; margin: 5px; border: 1px solid #ddd; border-radius: 4px; 
        }
        .status { padding: 10px; margin: 10px 0; border-radius: 4px; }
        .status.pending { background: #fff3cd; border: 1px solid #ffeaa7; }
        .status.progress { background: #d1ecf1; border: 1px solid #bee5eb; }
        .status.success { background: #d4edda; border: 1px solid #c3e6cb; }
        .status.failure { background: #f8d7da; border: 1px solid #f5c6cb; }
    </style>
    <script>
        function executeTask(url, params = {}) {
            const resultDiv = document.getElementById('result');
            resultDiv.innerHTML = '<div class="status pending">Executing task...</div>';
            
            fetch(url, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(params)
            })
            .then(response => response.json())
            .then(data => {
                resultDiv.innerHTML = '<div class="result">' + JSON.stringify(data, null, 2) + '</div>';
                if (data.task_id) {
                    checkTaskStatus(data.task_id);
                }
            })
            .catch(error => {
                resultDiv.innerHTML = '<div class="status failure">Error: ' + error + '</div>';
            });
        }
        
        function checkTaskStatus(taskId, interval = 1000) {
            const statusCheck = () => {
                fetch('/task-status/' + taskId)
                .then(response => response.json())
                .then(data => {
                    const statusDiv = document.getElementById('status');
                    if (data.state === 'PENDING') {
                        statusDiv.innerHTML = '<div class="status pending">Task is pending...</div>';
                        setTimeout(statusCheck, interval);
                    } else if (data.state === 'PROGRESS') {
                        statusDiv.innerHTML = '<div class="status progress">Progress: ' + 
                            data.current + '/' + data.total + ' - ' + data.status + '</div>';
                        setTimeout(statusCheck, interval);
                    } else if (data.state === 'SUCCESS') {
                        statusDiv.innerHTML = '<div class="status success">Task completed successfully!</div>' +
                            '<div class="result">' + JSON.stringify(data.result, null, 2) + '</div>';
                    } else {
                        statusDiv.innerHTML = '<div class="status failure">Task failed: ' + data.result + '</div>';
                    }
                });
            };
            statusCheck();
        }
        
        function executeTaskWithInputs(url, inputIds) {
            const params = {};
            inputIds.forEach(id => {
                const element = document.getElementById(id);
                params[id] = element.type === 'number' ? parseFloat(element.value) : element.value;
            });
            executeTask(url, params);
        }
    </script>
</head>
<body>
    <div class="container">
        <h1>Celery Sample Application</h1>
        <p>This application demonstrates various Celery task execution patterns using Redis as the message broker.</p>
        
        <div id="result"></div>
        <div id="status"></div>
        
        <div class="task-section">
            <h3>Basic Math Operations</h3>
            <p>Simple tasks that perform basic mathematical operations.</p>
            <input type="number" id="x" value="10" placeholder="First number">
            <input type="number" id="y" value="5" placeholder="Second number">
            <br>
            <button onclick="executeTaskWithInputs('/add', ['x', 'y'])">Add Numbers</button>
            <button onclick="executeTaskWithInputs('/multiply', ['x', 'y'])">Multiply Numbers</button>
        </div>
        
        <div class="task-section">
            <h3>Long-Running Task</h3>
            <p>Demonstrates progress tracking for long-running tasks.</p>
            <input type="number" id="duration" value="5" placeholder="Duration in seconds">
            <br>
            <button onclick="executeTaskWithInputs('/long-task', ['duration'])">Start Long Task</button>
        </div>
        
        <div class="task-section">
            <h3>Data Processing</h3>
            <p>Generate random data and process it.</p>
            <input type="number" id="count" value="50" placeholder="Number of data points">
            <br>
            <button onclick="executeTaskWithInputs('/generate-data', ['count'])">Generate Random Data</button>
            <button onclick="executeTask('/process-workflow')">Data Processing Workflow</button>
        </div>
        
        <div class="task-section">
            <h3>Task Chaining</h3>
            <p>Demonstrates chaining multiple tasks together.</p>
            <input type="number" id="chain_input" value="5" placeholder="Input number">
            <br>
            <button onclick="executeTaskWithInputs('/chain-tasks', ['chain_input'])">Execute Task Chain</button>
        </div>
        
        <div class="task-section">
            <h3>Error Handling</h3>
            <p>Demonstrates retry behavior for failing tasks.</p>
            <button onclick="executeTask('/failing-task')">Execute Failing Task</button>
        </div>
        
        <div class="task-section">
            <h3>Task Status</h3>
            <p>Check the status of any task by ID.</p>
            <input type="text" id="task_id" placeholder="Task ID">
            <button onclick="checkTaskStatus(document.getElementById('task_id').value)">Check Status</button>
        </div>
    </div>
</body>
</html>
"""


@app.route("/")
def home():
    """Home page with task execution interface."""
    return render_template_string(HTML_TEMPLATE)


@app.route("/add", methods=["POST"])
def add():
    """Execute add_numbers task."""
    data = request.json or {}
    x = data.get("x", 10)
    y = data.get("y", 5)

    task = add_numbers.delay(x, y)
    return jsonify({"task_id": task.id, "status": "Task submitted", "task": "add_numbers", "params": {"x": x, "y": y}})


@app.route("/multiply", methods=["POST"])
def multiply():
    """Execute multiply_numbers task."""
    data = request.json or {}
    x = data.get("x", 10)
    y = data.get("y", 5)

    task = multiply_numbers.delay(x, y)
    return jsonify(
        {"task_id": task.id, "status": "Task submitted", "task": "multiply_numbers", "params": {"x": x, "y": y}}
    )


@app.route("/long-task", methods=["POST"])
def long_task():
    """Execute long_running_task."""
    data = request.json or {}
    duration = data.get("duration", 5)

    task = long_running_task.delay(duration)
    return jsonify(
        {
            "task_id": task.id,
            "status": "Long-running task submitted",
            "task": "long_running_task",
            "params": {"duration": duration},
        }
    )


@app.route("/generate-data", methods=["POST"])
def generate_data():
    """Execute generate_random_data task."""
    data = request.json or {}
    count = data.get("count", 100)

    task = generate_random_data.delay(count)
    return jsonify(
        {
            "task_id": task.id,
            "status": "Data generation task submitted",
            "task": "generate_random_data",
            "params": {"count": count},
        }
    )


@app.route("/process-workflow", methods=["POST"])
def process_workflow():
    """Execute a workflow that generates data and then processes it."""
    # Use chord to run data generation and then process the result
    job = chord([generate_random_data.s(50), generate_random_data.s(30)])(process_data.s())

    return jsonify(
        {
            "task_id": job.id,
            "status": "Data processing workflow submitted",
            "task": "chord(generate_random_data) | process_data",
        }
    )


@app.route("/chain-tasks", methods=["POST"])
def chain_tasks():
    """Execute a chain of tasks."""
    data = request.json or {}
    input_value = data.get("chain_input", 5)

    # Chain three tasks together
    job = chain(chain_example.s(input_value), chain_example.s(), chain_example.s())()

    return jsonify(
        {
            "task_id": job.id,
            "status": "Task chain submitted",
            "task": "chain(chain_example * 3)",
            "params": {"input": input_value},
        }
    )


@app.route("/failing-task", methods=["POST"])
def failing_task_endpoint():
    """Execute failing_task to demonstrate retry behavior."""
    task = failing_task.delay()
    return jsonify(
        {"task_id": task.id, "status": "Failing task submitted (will retry on failure)", "task": "failing_task"}
    )


@app.route("/task-status/<task_id>")
def task_status(task_id):
    """Get the status of a task."""
    task = celery_app.AsyncResult(task_id)

    if task.state == "PENDING":
        response = {"state": task.state, "current": 0, "total": 1, "status": "Pending..."}
    elif task.state == "PROGRESS":
        response = {
            "state": task.state,
            "current": task.info.get("current", 0),
            "total": task.info.get("total", 1),
            "status": task.info.get("status", ""),
        }
    elif task.state == "SUCCESS":
        response = {"state": task.state, "result": task.result}
    else:
        # Task failed
        response = {"state": task.state, "result": str(task.info)}  # Exception info

    return jsonify(response)


@app.route("/worker-status")
def worker_status():
    """Get information about active Celery workers."""
    inspect = celery_app.control.inspect()

    return jsonify(
        {"active_workers": inspect.active(), "registered_tasks": inspect.registered(), "stats": inspect.stats()}
    )


if __name__ == "__main__":
    print("Starting Celery Sample Flask App...")
    print("Make sure Redis is running and Celery worker is started!")
    print("Visit http://localhost:5000 to interact with Celery tasks")
    app.run(debug=True, host="0.0.0.0", port=5000)
