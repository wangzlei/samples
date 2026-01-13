#!/usr/bin/env python3
"""
Flask application that demonstrates Pika (RabbitMQ) message publishing and consuming.

This Flask app provides a web interface to:
- Send messages to RabbitMQ queues
- Monitor queue status
- Demonstrate various messaging patterns

To run:
    1. Start RabbitMQ: docker-compose up -d
    2. Start Flask app: python app.py
    3. Visit http://localhost:5000
"""

import json
import threading
import time
from datetime import datetime

import pika
from flask import Flask, jsonify, render_template_string, request
from pika.exceptions import AMQPChannelError, AMQPConnectionError

app = Flask(__name__)

# Global variables for RabbitMQ connection
connection = None
channel = None
consumer_thread = None
received_messages = []

# HTML template for the web interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Pika (RabbitMQ) Sample App</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .container { max-width: 900px; margin: 0 auto; }
        .section { margin: 30px 0; padding: 20px; background: #f8f9fa; border-radius: 8px; }
        .section h3 { margin-top: 0; color: #2c3e50; }
        button { 
            background: #28a745; color: white; border: none; padding: 10px 20px; 
            border-radius: 4px; cursor: pointer; margin: 5px; 
        }
        button:hover { background: #218838; }
        .danger { background: #dc3545; }
        .danger:hover { background: #c82333; }
        .result { 
            margin: 10px 0; padding: 10px; background: #e9ecef; 
            border-radius: 4px; font-family: monospace; max-height: 200px; overflow-y: auto;
        }
        input, textarea { 
            padding: 8px; margin: 5px; border: 1px solid #ddd; border-radius: 4px; width: 200px;
        }
        textarea { width: 300px; height: 80px; }
        .status { padding: 10px; margin: 10px 0; border-radius: 4px; }
        .status.success { background: #d4edda; border: 1px solid #c3e6cb; }
        .status.error { background: #f8d7da; border: 1px solid #f5c6cb; }
        .status.info { background: #d1ecf1; border: 1px solid #bee5eb; }
        .messages { max-height: 300px; overflow-y: auto; }
        .message { padding: 8px; margin: 5px 0; background: #fff; border: 1px solid #ddd; border-radius: 4px; }
    </style>
    <script>
        function sendRequest(url, data = {}) {
            const resultDiv = document.getElementById('result');
            resultDiv.innerHTML = '<div class="status info">Processing...</div>';
            
            fetch(url, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(data => {
                resultDiv.innerHTML = '<div class="result">' + JSON.stringify(data, null, 2) + '</div>';
                if (data.status === 'success') {
                    resultDiv.firstChild.className = 'status success';
                } else if (data.status === 'error') {
                    resultDiv.firstChild.className = 'status error';
                }
            })
            .catch(error => {
                resultDiv.innerHTML = '<div class="status error">Error: ' + error + '</div>';
            });
        }
        
        function publishMessage() {
            const queue = document.getElementById('queue').value;
            const message = document.getElementById('message').value;
            sendRequest('/publish', {queue: queue, message: message});
        }
        
        function refreshMessages() {
            fetch('/messages')
            .then(response => response.json())
            .then(data => {
                const messagesDiv = document.getElementById('messages');
                messagesDiv.innerHTML = '';
                data.messages.forEach(msg => {
                    const div = document.createElement('div');
                    div.className = 'message';
                    div.innerHTML = '<strong>' + msg.timestamp + '</strong> [' + msg.queue + ']: ' + msg.body;
                    messagesDiv.appendChild(div);
                });
            });
        }
        
        function getQueueInfo() {
            const queue = document.getElementById('info_queue').value;
            sendRequest('/queue-info', {queue: queue});
        }
        
        // Auto-refresh messages every 2 seconds
        setInterval(refreshMessages, 2000);
        
        // Initial load
        window.onload = function() {
            refreshMessages();
            sendRequest('/connection-status');
        };
    </script>
</head>
<body>
    <div class="container">
        <h1>Pika (RabbitMQ) Sample Application</h1>
        <p>This application demonstrates RabbitMQ messaging using the Pika Python library.</p>
        
        <div id="result"></div>
        
        <div class="section">
            <h3>Connection Management</h3>
            <p>Manage RabbitMQ connection and setup.</p>
            <button onclick="sendRequest('/connect')">Connect to RabbitMQ</button>
            <button onclick="sendRequest('/disconnect')" class="danger">Disconnect</button>
            <button onclick="sendRequest('/connection-status')">Check Status</button>
        </div>
        
        <div class="section">
            <h3>Queue Management</h3>
            <p>Create and manage RabbitMQ queues.</p>
            <input type="text" id="create_queue" value="demo_queue" placeholder="Queue name">
            <button onclick="sendRequest('/create-queue', {queue: document.getElementById('create_queue').value})">Create Queue</button>
            <br><br>
            <input type="text" id="info_queue" value="demo_queue" placeholder="Queue name">
            <button onclick="getQueueInfo()">Get Queue Info</button>
        </div>
        
        <div class="section">
            <h3>Message Publishing</h3>
            <p>Send messages to RabbitMQ queues.</p>
            <input type="text" id="queue" value="demo_queue" placeholder="Queue name">
            <br>
            <textarea id="message" placeholder="Message content">{"hello": "world", "timestamp": "2024-01-01"}</textarea>
            <br>
            <button onclick="publishMessage()">Publish Message</button>
            <button onclick="sendRequest('/publish-batch', {queue: document.getElementById('queue').value, count: 5})">Publish 5 Messages</button>
        </div>
        
        <div class="section">
            <h3>Consumer Management</h3>
            <p>Start and stop message consumers.</p>
            <input type="text" id="consumer_queue" value="demo_queue" placeholder="Queue name">
            <button onclick="sendRequest('/start-consumer', {queue: document.getElementById('consumer_queue').value})">Start Consumer</button>
            <button onclick="sendRequest('/stop-consumer')" class="danger">Stop Consumer</button>
        </div>
        
        <div class="section">
            <h3>Received Messages</h3>
            <p>Messages received by the consumer (auto-refreshes every 2 seconds).</p>
            <button onclick="refreshMessages()">Refresh</button>
            <button onclick="sendRequest('/clear-messages')" class="danger">Clear Messages</button>
            <div id="messages" class="messages"></div>
        </div>
    </div>
</body>
</html>
"""


def get_rabbitmq_connection():
    """Get RabbitMQ connection."""
    global connection, channel
    try:
        if connection is None or connection.is_closed:
            connection_params = pika.ConnectionParameters(
                host="localhost", port=5672, heartbeat=600, blocked_connection_timeout=300
            )
            connection = pika.BlockingConnection(connection_params)
            channel = connection.channel()
        return connection, channel
    except AMQPConnectionError as e:
        return None, None


def close_rabbitmq_connection():
    """Close RabbitMQ connection."""
    global connection, channel
    if connection and not connection.is_closed:
        connection.close()
        connection = None
        channel = None


def consumer_worker(queue_name):
    """Worker function for consuming messages."""
    global received_messages
    try:
        conn, ch = get_rabbitmq_connection()
        if not conn:
            return

        def callback(ch, method, properties, body):
            message = {
                "timestamp": datetime.now().strftime("%H:%M:%S"),
                "queue": queue_name,
                "body": body.decode("utf-8"),
                "delivery_tag": method.delivery_tag,
            }
            received_messages.append(message)
            # Keep only the last 50 messages
            if len(received_messages) > 50:
                received_messages.pop(0)
            ch.basic_ack(delivery_tag=method.delivery_tag)

        ch.basic_consume(queue=queue_name, on_message_callback=callback)
        ch.start_consuming()

    except Exception as e:
        print(f"Consumer error: {e}")


@app.route("/")
def home():
    """Home page with RabbitMQ interface."""
    return render_template_string(HTML_TEMPLATE)


@app.route("/connect", methods=["POST"])
def connect():
    """Connect to RabbitMQ."""
    try:
        conn, ch = get_rabbitmq_connection()
        if conn:
            return jsonify(
                {
                    "status": "success",
                    "message": "Connected to RabbitMQ successfully",
                    "connection_info": {"host": "localhost", "port": 5672, "is_open": conn.is_open},
                }
            )
        else:
            return jsonify(
                {"status": "error", "message": "Failed to connect to RabbitMQ. Make sure RabbitMQ is running."}
            )
    except Exception as e:
        return jsonify({"status": "error", "message": f"Connection error: {str(e)}"})


@app.route("/disconnect", methods=["POST"])
def disconnect():
    """Disconnect from RabbitMQ."""
    global consumer_thread
    try:
        # Stop consumer if running
        if consumer_thread and consumer_thread.is_alive():
            if channel:
                channel.stop_consuming()
            consumer_thread = None

        close_rabbitmq_connection()
        return jsonify({"status": "success", "message": "Disconnected from RabbitMQ"})
    except Exception as e:
        return jsonify({"status": "error", "message": f"Disconnect error: {str(e)}"})


@app.route("/connection-status", methods=["POST"])
def connection_status():
    """Check RabbitMQ connection status."""
    global connection
    try:
        if connection and not connection.is_closed:
            return jsonify(
                {
                    "status": "success",
                    "connected": True,
                    "message": "Connected to RabbitMQ",
                    "connection_info": {"is_open": connection.is_open, "host": "localhost", "port": 5672},
                }
            )
        else:
            return jsonify({"status": "info", "connected": False, "message": "Not connected to RabbitMQ"})
    except Exception as e:
        return jsonify({"status": "error", "connected": False, "message": f"Status check error: {str(e)}"})


@app.route("/create-queue", methods=["POST"])
def create_queue():
    """Create a RabbitMQ queue."""
    try:
        data = request.json or {}
        queue_name = data.get("queue", "demo_queue")

        conn, ch = get_rabbitmq_connection()
        if not conn:
            return jsonify({"status": "error", "message": "Not connected to RabbitMQ"})

        ch.queue_declare(queue=queue_name, durable=True)
        return jsonify(
            {"status": "success", "message": f'Queue "{queue_name}" created successfully', "queue": queue_name}
        )
    except Exception as e:
        return jsonify({"status": "error", "message": f"Queue creation error: {str(e)}"})


@app.route("/queue-info", methods=["POST"])
def queue_info():
    """Get information about a queue."""
    try:
        data = request.json or {}
        queue_name = data.get("queue", "demo_queue")

        conn, ch = get_rabbitmq_connection()
        if not conn:
            return jsonify({"status": "error", "message": "Not connected to RabbitMQ"})

        method = ch.queue_declare(queue=queue_name, durable=True, passive=True)
        return jsonify(
            {
                "status": "success",
                "queue": queue_name,
                "message_count": method.method.message_count,
                "consumer_count": method.method.consumer_count,
            }
        )
    except Exception as e:
        return jsonify({"status": "error", "message": f"Queue info error: {str(e)}"})


@app.route("/publish", methods=["POST"])
def publish():
    """Publish a message to a queue."""
    try:
        data = request.json or {}
        queue_name = data.get("queue", "demo_queue")
        message = data.get("message", '{"hello": "world"}')

        conn, ch = get_rabbitmq_connection()
        if not conn:
            return jsonify({"status": "error", "message": "Not connected to RabbitMQ"})

        # Ensure queue exists
        ch.queue_declare(queue=queue_name, durable=True)

        # Publish message
        ch.basic_publish(
            exchange="",
            routing_key=queue_name,
            body=message,
            properties=pika.BasicProperties(delivery_mode=2),  # Make message persistent
        )

        return jsonify(
            {
                "status": "success",
                "message": f'Message published to "{queue_name}"',
                "queue": queue_name,
                "published_message": message,
                "timestamp": datetime.now().strftime("%H:%M:%S"),
            }
        )
    except Exception as e:
        return jsonify({"status": "error", "message": f"Publish error: {str(e)}"})


@app.route("/publish-batch", methods=["POST"])
def publish_batch():
    """Publish multiple messages to a queue."""
    try:
        data = request.json or {}
        queue_name = data.get("queue", "demo_queue")
        count = data.get("count", 5)

        conn, ch = get_rabbitmq_connection()
        if not conn:
            return jsonify({"status": "error", "message": "Not connected to RabbitMQ"})

        # Ensure queue exists
        ch.queue_declare(queue=queue_name, durable=True)

        # Publish multiple messages
        for i in range(count):
            message = json.dumps(
                {"id": i + 1, "message": f"Batch message {i + 1}", "timestamp": datetime.now().isoformat()}
            )
            ch.basic_publish(
                exchange="", routing_key=queue_name, body=message, properties=pika.BasicProperties(delivery_mode=2)
            )

        return jsonify(
            {
                "status": "success",
                "message": f'{count} messages published to "{queue_name}"',
                "queue": queue_name,
                "count": count,
                "timestamp": datetime.now().strftime("%H:%M:%S"),
            }
        )
    except Exception as e:
        return jsonify({"status": "error", "message": f"Batch publish error: {str(e)}"})


@app.route("/start-consumer", methods=["POST"])
def start_consumer():
    """Start consuming messages from a queue."""
    global consumer_thread
    try:
        data = request.json or {}
        queue_name = data.get("queue", "demo_queue")

        conn, ch = get_rabbitmq_connection()
        if not conn:
            return jsonify({"status": "error", "message": "Not connected to RabbitMQ"})

        # Stop existing consumer if running
        if consumer_thread and consumer_thread.is_alive():
            if channel:
                channel.stop_consuming()

        # Ensure queue exists
        ch.queue_declare(queue=queue_name, durable=True)

        # Start consumer in a separate thread
        consumer_thread = threading.Thread(target=consumer_worker, args=(queue_name,), daemon=True)
        consumer_thread.start()

        return jsonify(
            {
                "status": "success",
                "message": f'Consumer started for queue "{queue_name}"',
                "queue": queue_name,
                "timestamp": datetime.now().strftime("%H:%M:%S"),
            }
        )
    except Exception as e:
        return jsonify({"status": "error", "message": f"Consumer start error: {str(e)}"})


@app.route("/stop-consumer", methods=["POST"])
def stop_consumer():
    """Stop the message consumer."""
    global consumer_thread
    try:
        if consumer_thread and consumer_thread.is_alive():
            if channel:
                channel.stop_consuming()
            consumer_thread = None
            return jsonify(
                {"status": "success", "message": "Consumer stopped", "timestamp": datetime.now().strftime("%H:%M:%S")}
            )
        else:
            return jsonify({"status": "info", "message": "No consumer is currently running"})
    except Exception as e:
        return jsonify({"status": "error", "message": f"Consumer stop error: {str(e)}"})


@app.route("/messages", methods=["GET"])
def get_messages():
    """Get received messages."""
    global received_messages
    return jsonify(
        {"messages": received_messages[-20:], "total_count": len(received_messages)}  # Return last 20 messages
    )


@app.route("/clear-messages", methods=["POST"])
def clear_messages():
    """Clear received messages."""
    global received_messages
    received_messages.clear()
    return jsonify({"status": "success", "message": "Messages cleared"})


if __name__ == "__main__":
    print("Starting Pika (RabbitMQ) Sample Flask App...")
    print("Make sure RabbitMQ is running! Use 'docker-compose up -d' to start RabbitMQ")
    print("Visit http://localhost:5000 to interact with RabbitMQ")
    app.run(debug=True, host="0.0.0.0", port=5000)
