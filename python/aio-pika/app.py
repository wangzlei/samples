#!/usr/bin/env python3
"""
Flask application that demonstrates aio-pika (async RabbitMQ) message publishing and consuming.

This Flask app provides a web interface to:
- Send messages to RabbitMQ queues using async operations
- Monitor queue status
- Demonstrate various async messaging patterns

To run:
    1. Start RabbitMQ: docker-compose up -d
    2. Start Flask app: python app.py
    3. Visit http://localhost:5000
"""

import asyncio
import json
import threading
import time
from datetime import datetime

import aio_pika
from aio_pika.exceptions import AMQPException
from flask import Flask, jsonify, render_template_string, request

app = Flask(__name__)

# Global variables for RabbitMQ connection
connection = None
channel = None
consumer_task = None
received_messages = []
event_loop = None
loop_thread = None

# HTML template for the web interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>aio-pika (Async RabbitMQ) Sample App</title>
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
        .async-note { background: #fff3cd; border: 1px solid #ffeaa7; padding: 10px; margin: 10px 0; border-radius: 4px; }
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
        <h1>aio-pika (Async RabbitMQ) Sample Application</h1>
        <p>This application demonstrates async RabbitMQ messaging using the aio-pika Python library.</p>
        
        <div class="async-note">
            <strong>Note:</strong> This sample uses aio-pika for asynchronous RabbitMQ operations. 
            All message publishing and consuming operations are handled asynchronously for better performance.
        </div>
        
        <div id="result"></div>
        
        <div class="section">
            <h3>Connection Management</h3>
            <p>Manage async RabbitMQ connection and setup.</p>
            <button onclick="sendRequest('/connect')">Connect to RabbitMQ</button>
            <button onclick="sendRequest('/disconnect')" class="danger">Disconnect</button>
            <button onclick="sendRequest('/connection-status')">Check Status</button>
        </div>
        
        <div class="section">
            <h3>Queue Management</h3>
            <p>Create and manage RabbitMQ queues asynchronously.</p>
            <input type="text" id="create_queue" value="demo_queue" placeholder="Queue name">
            <button onclick="sendRequest('/create-queue', {queue: document.getElementById('create_queue').value})">Create Queue</button>
            <br><br>
            <input type="text" id="info_queue" value="demo_queue" placeholder="Queue name">
            <button onclick="getQueueInfo()">Get Queue Info</button>
        </div>
        
        <div class="section">
            <h3>Async Message Publishing</h3>
            <p>Send messages to RabbitMQ queues asynchronously.</p>
            <input type="text" id="queue" value="demo_queue" placeholder="Queue name">
            <br>
            <textarea id="message" placeholder="Message content">{"hello": "world", "timestamp": "2024-01-01", "async": true}</textarea>
            <br>
            <button onclick="publishMessage()">Publish Message</button>
            <button onclick="sendRequest('/publish-batch', {queue: document.getElementById('queue').value, count: 5})">Publish 5 Messages</button>
        </div>
        
        <div class="section">
            <h3>Async Consumer Management</h3>
            <p>Start and stop async message consumers.</p>
            <input type="text" id="consumer_queue" value="demo_queue" placeholder="Queue name">
            <button onclick="sendRequest('/start-consumer', {queue: document.getElementById('consumer_queue').value})">Start Consumer</button>
            <button onclick="sendRequest('/stop-consumer')" class="danger">Stop Consumer</button>
        </div>
        
        <div class="section">
            <h3>Received Messages</h3>
            <p>Messages received by the async consumer (auto-refreshes every 2 seconds).</p>
            <button onclick="refreshMessages()">Refresh</button>
            <button onclick="sendRequest('/clear-messages')" class="danger">Clear Messages</button>
            <div id="messages" class="messages"></div>
        </div>
    </div>
</body>
</html>
"""


def run_async_in_thread(coro):
    """Run async function in the event loop thread."""
    if event_loop and not event_loop.is_closed():
        future = asyncio.run_coroutine_threadsafe(coro, event_loop)
        return future.result(timeout=10)
    else:
        raise RuntimeError("Event loop not available")


async def get_rabbitmq_connection():
    """Get async RabbitMQ connection."""
    global connection, channel
    try:
        if connection is None or connection.is_closed:
            connection = await aio_pika.connect_robust("amqp://guest:guest@localhost:5672/", heartbeat=600)
            channel = await connection.channel()
            await channel.set_qos(prefetch_count=1)
        return connection, channel
    except Exception as e:
        print(f"Connection error: {e}")
        return None, None


async def close_rabbitmq_connection():
    """Close async RabbitMQ connection."""
    global connection, channel, consumer_task

    # Cancel consumer task
    if consumer_task and not consumer_task.done():
        consumer_task.cancel()
        try:
            await consumer_task
        except asyncio.CancelledError:
            pass
        consumer_task = None

    # Close channel and connection
    if channel and not channel.is_closed:
        await channel.close()
        channel = None

    if connection and not connection.is_closed:
        await connection.close()
        connection = None


async def consumer_worker(queue_name):
    """Async worker function for consuming messages."""
    global received_messages
    try:
        conn, ch = await get_rabbitmq_connection()
        if not conn:
            return

        queue = await ch.declare_queue(queue_name, durable=True)

        async def message_callback(message: aio_pika.IncomingMessage):
            async with message.process():
                msg_data = {
                    "timestamp": datetime.now().strftime("%H:%M:%S"),
                    "queue": queue_name,
                    "body": message.body.decode("utf-8"),
                    "delivery_tag": message.delivery_tag,
                }
                received_messages.append(msg_data)
                # Keep only the last 50 messages
                if len(received_messages) > 50:
                    received_messages.pop(0)
                print(f"Received message: {msg_data['body']}")

        # Start consuming
        await queue.consume(message_callback)
        print(f"Started consuming from queue: {queue_name}")

        # Keep the consumer running
        while True:
            await asyncio.sleep(1)

    except asyncio.CancelledError:
        print("Consumer cancelled")
        raise
    except Exception as e:
        print(f"Consumer error: {e}")


def start_event_loop():
    """Start the async event loop in a separate thread."""
    global event_loop
    event_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(event_loop)
    event_loop.run_forever()


def init_async_loop():
    """Initialize the async event loop thread."""
    global loop_thread, event_loop
    if loop_thread is None or not loop_thread.is_alive():
        loop_thread = threading.Thread(target=start_event_loop, daemon=True)
        loop_thread.start()
        # Wait a bit for the loop to start
        time.sleep(0.1)


@app.route("/")
def home():
    """Home page with async RabbitMQ interface."""
    return render_template_string(HTML_TEMPLATE)


@app.route("/connect", methods=["POST"])
def connect():
    """Connect to RabbitMQ asynchronously."""
    try:
        init_async_loop()

        async def async_connect():
            conn, ch = await get_rabbitmq_connection()
            if conn:
                return {
                    "status": "success",
                    "message": "Connected to RabbitMQ successfully (async)",
                    "connection_info": {
                        "host": "localhost",
                        "port": 5672,
                        "is_open": not conn.is_closed,
                        "library": "aio-pika",
                    },
                }
            else:
                return {"status": "error", "message": "Failed to connect to RabbitMQ. Make sure RabbitMQ is running."}

        result = run_async_in_thread(async_connect())
        return jsonify(result)
    except Exception as e:
        return jsonify({"status": "error", "message": f"Connection error: {str(e)}"})


@app.route("/disconnect", methods=["POST"])
def disconnect():
    """Disconnect from RabbitMQ asynchronously."""
    try:

        async def async_disconnect():
            await close_rabbitmq_connection()
            return {"status": "success", "message": "Disconnected from RabbitMQ (async)"}

        result = run_async_in_thread(async_disconnect())
        return jsonify(result)
    except Exception as e:
        return jsonify({"status": "error", "message": f"Disconnect error: {str(e)}"})


@app.route("/connection-status", methods=["POST"])
def connection_status():
    """Check async RabbitMQ connection status."""
    global connection
    try:
        if connection and not connection.is_closed:
            return jsonify(
                {
                    "status": "success",
                    "connected": True,
                    "message": "Connected to RabbitMQ (async)",
                    "connection_info": {
                        "is_open": not connection.is_closed,
                        "host": "localhost",
                        "port": 5672,
                        "library": "aio-pika",
                    },
                }
            )
        else:
            return jsonify({"status": "info", "connected": False, "message": "Not connected to RabbitMQ (async)"})
    except Exception as e:
        return jsonify({"status": "error", "connected": False, "message": f"Status check error: {str(e)}"})


@app.route("/create-queue", methods=["POST"])
def create_queue():
    """Create a RabbitMQ queue asynchronously."""
    try:
        data = request.json or {}
        queue_name = data.get("queue", "demo_queue")

        async def async_create_queue():
            conn, ch = await get_rabbitmq_connection()
            if not conn:
                return {"status": "error", "message": "Not connected to RabbitMQ"}

            queue = await ch.declare_queue(queue_name, durable=True)
            return {
                "status": "success",
                "message": f'Queue "{queue_name}" created successfully (async)',
                "queue": queue_name,
            }

        result = run_async_in_thread(async_create_queue())
        return jsonify(result)
    except Exception as e:
        return jsonify({"status": "error", "message": f"Queue creation error: {str(e)}"})


@app.route("/queue-info", methods=["POST"])
def queue_info():
    """Get information about a queue asynchronously."""
    try:
        data = request.json or {}
        queue_name = data.get("queue", "demo_queue")

        async def async_queue_info():
            conn, ch = await get_rabbitmq_connection()
            if not conn:
                return {"status": "error", "message": "Not connected to RabbitMQ"}

            queue = await ch.declare_queue(queue_name, durable=True, passive=True)
            # Note: aio-pika doesn't directly expose message count like pika
            # This is a limitation of the async implementation
            return {
                "status": "success",
                "queue": queue_name,
                "message": "Queue exists and is accessible (async)",
                "note": "Message count not available with aio-pika passive declaration",
            }

        result = run_async_in_thread(async_queue_info())
        return jsonify(result)
    except Exception as e:
        return jsonify({"status": "error", "message": f"Queue info error: {str(e)}"})


@app.route("/publish", methods=["POST"])
def publish():
    """Publish a message to a queue asynchronously."""
    try:
        data = request.json or {}
        queue_name = data.get("queue", "demo_queue")
        message = data.get("message", '{"hello": "world", "async": true}')

        async def async_publish():
            conn, ch = await get_rabbitmq_connection()
            if not conn:
                return {"status": "error", "message": "Not connected to RabbitMQ"}

            # Ensure queue exists
            queue = await ch.declare_queue(queue_name, durable=True)

            # Publish message
            message_obj = aio_pika.Message(message.encode("utf-8"), delivery_mode=aio_pika.DeliveryMode.PERSISTENT)

            await ch.default_exchange.publish(message_obj, routing_key=queue_name)

            return {
                "status": "success",
                "message": f'Message published to "{queue_name}" (async)',
                "queue": queue_name,
                "published_message": message,
                "timestamp": datetime.now().strftime("%H:%M:%S"),
            }

        result = run_async_in_thread(async_publish())
        return jsonify(result)
    except Exception as e:
        return jsonify({"status": "error", "message": f"Publish error: {str(e)}"})


@app.route("/publish-batch", methods=["POST"])
def publish_batch():
    """Publish multiple messages to a queue asynchronously."""
    try:
        data = request.json or {}
        queue_name = data.get("queue", "demo_queue")
        count = data.get("count", 5)

        async def async_publish_batch():
            conn, ch = await get_rabbitmq_connection()
            if not conn:
                return {"status": "error", "message": "Not connected to RabbitMQ"}

            # Ensure queue exists
            queue = await ch.declare_queue(queue_name, durable=True)

            # Publish multiple messages asynchronously
            tasks = []
            for i in range(count):
                message_data = json.dumps(
                    {
                        "id": i + 1,
                        "message": f"Async batch message {i + 1}",
                        "timestamp": datetime.now().isoformat(),
                        "async": True,
                    }
                )
                message_obj = aio_pika.Message(
                    message_data.encode("utf-8"), delivery_mode=aio_pika.DeliveryMode.PERSISTENT
                )

                task = ch.default_exchange.publish(message_obj, routing_key=queue_name)
                tasks.append(task)

            # Wait for all messages to be published
            await asyncio.gather(*tasks)

            return {
                "status": "success",
                "message": f'{count} messages published to "{queue_name}" (async batch)',
                "queue": queue_name,
                "count": count,
                "timestamp": datetime.now().strftime("%H:%M:%S"),
            }

        result = run_async_in_thread(async_publish_batch())
        return jsonify(result)
    except Exception as e:
        return jsonify({"status": "error", "message": f"Batch publish error: {str(e)}"})


@app.route("/start-consumer", methods=["POST"])
def start_consumer():
    """Start consuming messages from a queue asynchronously."""
    global consumer_task
    try:
        data = request.json or {}
        queue_name = data.get("queue", "demo_queue")

        init_async_loop()

        async def async_start_consumer():
            global consumer_task

            conn, ch = await get_rabbitmq_connection()
            if not conn:
                return {"status": "error", "message": "Not connected to RabbitMQ"}

            # Stop existing consumer if running
            if consumer_task and not consumer_task.done():
                consumer_task.cancel()
                try:
                    await consumer_task
                except asyncio.CancelledError:
                    pass

            # Ensure queue exists
            await ch.declare_queue(queue_name, durable=True)

            # Start consumer task
            consumer_task = asyncio.create_task(consumer_worker(queue_name))

            return {
                "status": "success",
                "message": f'Async consumer started for queue "{queue_name}"',
                "queue": queue_name,
                "timestamp": datetime.now().strftime("%H:%M:%S"),
            }

        result = run_async_in_thread(async_start_consumer())
        return jsonify(result)
    except Exception as e:
        return jsonify({"status": "error", "message": f"Consumer start error: {str(e)}"})


@app.route("/stop-consumer", methods=["POST"])
def stop_consumer():
    """Stop the async message consumer."""
    global consumer_task
    try:

        async def async_stop_consumer():
            global consumer_task
            if consumer_task and not consumer_task.done():
                consumer_task.cancel()
                try:
                    await consumer_task
                except asyncio.CancelledError:
                    pass
                consumer_task = None
                return {
                    "status": "success",
                    "message": "Async consumer stopped",
                    "timestamp": datetime.now().strftime("%H:%M:%S"),
                }
            else:
                return {"status": "info", "message": "No async consumer is currently running"}

        result = run_async_in_thread(async_stop_consumer())
        return jsonify(result)
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
    print("Starting aio-pika (Async RabbitMQ) Sample Flask App...")
    print("Make sure RabbitMQ is running! Use 'docker-compose up -d' to start RabbitMQ")
    print("Visit http://localhost:5000 to interact with async RabbitMQ")
    print("This sample uses aio-pika for asynchronous RabbitMQ operations")

    # Initialize the async event loop
    init_async_loop()

    app.run(debug=True, host="0.0.0.0", port=5000)
