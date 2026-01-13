# aio-pika (Async RabbitMQ) Sample Application

This sample demonstrates how to use aio-pika, the asynchronous Python client for RabbitMQ message broker. The application showcases various async RabbitMQ messaging patterns including message publishing, consuming, queue management, and connection handling through a web interface.

## Features Demonstrated

- **Async Message Publishing**: Send individual messages or batches to RabbitMQ queues asynchronously
- **Async Message Consuming**: Real-time message consumption with automatic acknowledgment using async patterns
- **Async Queue Management**: Create queues and monitor queue statistics asynchronously
- **Async Connection Management**: Connect/disconnect to RabbitMQ with status monitoring using async operations
- **Web Interface**: Flask-based UI for interacting with async RabbitMQ operations
- **Real-time Updates**: Auto-refreshing message display
- **Error Handling**: Proper async connection and error management
- **Performance**: Better throughput with asynchronous operations compared to blocking I/O

## Prerequisites

- Python 3.7+
- Docker and Docker Compose (for RabbitMQ)
- pip for installing Python dependencies

## Setup and Installation

1. **Navigate to the aio-pika sample directory:**
   ```bash
   cd samples/aio-pika
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start RabbitMQ using Docker Compose:**
   ```bash
   docker-compose up -d
   ```
   
   This will start:
   - RabbitMQ server on port 5672
   - RabbitMQ Management UI on port 15672

4. **Verify RabbitMQ is running:**
   ```bash
   docker-compose ps
   ```

## Running the Application

### Start the Flask Web Application

```bash
cd samples/aio-pika
python app.py
```

The Flask app will start on http://localhost:5000

## Using the Application

1. **Open the Web Interface**: Visit http://localhost:5000 in your browser

2. **Connect to RabbitMQ**: Click "Connect to RabbitMQ" to establish async connection

3. **Create Queues**: Use the Queue Management section to create new queues asynchronously

4. **Publish Messages**: 
   - Send individual messages with custom content asynchronously
   - Publish multiple messages in batch with concurrent operations

5. **Start Consumer**: Begin consuming messages from a queue to see real-time async message processing

6. **Monitor Activity**: 
   - View received messages in real-time
   - Check queue information 
   - Monitor async connection status

## Application Sections

### Async Connection Management
- Connect/disconnect to RabbitMQ asynchronously
- Check connection status with async operations
- View connection information including library details

### Async Queue Management
- Create durable queues asynchronously
- Get queue information with async operations
- Monitor queue statistics

### Async Message Publishing
- Publish individual messages with custom content asynchronously
- Batch publish multiple messages with concurrent operations
- JSON message format support with async flag
- Better performance through non-blocking operations

### Async Consumer Management
- Start/stop message consumers asynchronously
- Real-time message processing with async callbacks
- Automatic message acknowledgment
- Graceful consumer cancellation

### Message Monitoring
- View received messages in real-time
- Auto-refresh every 2 seconds
- Clear message history
- Shows async processing timestamps

## Additional Monitoring Tools

- **RabbitMQ Management UI**: http://localhost:15672 (guest/guest)
  - View queues, exchanges, and connections
  - Monitor message rates and statistics
  - Manage RabbitMQ configuration

## Message Flow

1. **Publishing**: Messages are sent to named queues asynchronously with persistence enabled
2. **Queuing**: RabbitMQ stores messages in durable queues
3. **Consuming**: Async consumer tasks process messages and acknowledge them
4. **Monitoring**: Web interface displays real-time message activity

## Async Configuration

The aio-pika configuration in the application:

- **Host**: localhost
- **Port**: 5672
- **Connection Parameters**:
  - Heartbeat: 600 seconds
  - Robust connection with automatic reconnection
- **Queue Settings**: Durable queues for message persistence
- **Message Properties**: Persistent messages (DeliveryMode.PERSISTENT)
- **QoS**: Prefetch count of 1 for better load balancing
- **Event Loop**: Dedicated thread for async operations

## Key Async Features

### Asynchronous Operations
- Non-blocking connection establishment
- Concurrent message publishing
- Async message consumption with callbacks
- Event loop management in separate thread

### Performance Benefits
- Better throughput with concurrent operations
- Non-blocking I/O for improved responsiveness
- Efficient resource utilization
- Scalable message processing

### Robust Connection Handling
- Automatic reconnection on connection failures
- Graceful handling of network interruptions
- Proper cleanup of async resources

## Troubleshooting

### Common Issues

1. **RabbitMQ Connection Error**:
   - Ensure RabbitMQ is running: `docker-compose ps`
   - Check RabbitMQ logs: `docker-compose logs rabbitmq`
   - Verify port 5672 is not blocked

2. **Async Consumer Not Receiving Messages**:
   - Make sure async consumer is started
   - Check if messages are being published to the correct queue
   - Verify queue exists and has messages
   - Check event loop is running properly

3. **Web Interface Issues**:
   - Ensure Flask app is running on port 5000
   - Check browser console for JavaScript errors
   - Try refreshing the page
   - Verify async operations are completing

4. **Import Errors**:
   - Ensure all dependencies are installed: `pip install -r requirements.txt`
   - Check Python version compatibility (3.7+)
   - Verify aio-pika version (9.0.0+)

5. **Async Event Loop Issues**:
   - Check if event loop thread is running
   - Verify no event loop conflicts
   - Monitor for async operation timeouts

### Useful Commands

```bash
# Check RabbitMQ status
docker-compose ps

# View RabbitMQ logs
docker-compose logs rabbitmq

# Restart RabbitMQ
docker-compose restart rabbitmq

# Stop all services
docker-compose down

# Remove volumes (deletes RabbitMQ data)
docker-compose down -v
```

### RabbitMQ Management Commands

Access the RabbitMQ container for management:

```bash
# Enter RabbitMQ container
docker exec -it aio-pika-sample-rabbitmq bash

# List queues
rabbitmqctl list_queues

# List exchanges
rabbitmqctl list_exchanges

# Check cluster status
rabbitmqctl cluster_status
```

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Flask App     │    │   RabbitMQ      │    │  Async Consumer │
│   (Web UI)      │────│   (Message      │────│   (Event Loop   │
│   Port 5000     │    │    Broker)      │    │    Thread)      │
│                 │    │   Port 5672     │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐              │
         └──────────────│  Management UI  │──────────────┘
                        │   Port 15672    │
                        └─────────────────┘
                                 │
                        ┌─────────────────┐
                        │  Event Loop     │
                        │  (Async Ops)    │
                        └─────────────────┘
```

## Async Message Patterns

### Basic Async Queue Pattern
- Producer sends messages to a named queue asynchronously
- Consumer processes messages from the queue with async callbacks
- Messages are acknowledged after processing asynchronously

### Async Batch Processing
- Multiple messages published concurrently
- Consumer processes each message individually with async handlers
- Automatic acknowledgment ensures message delivery

### Event Loop Integration
- Dedicated event loop thread for async operations
- Thread-safe async operation execution
- Proper resource cleanup and cancellation

## Comparison with Synchronous Pika

| Feature | aio-pika (Async) | pika (Sync) |
|---------|------------------|-------------|
| I/O Model | Non-blocking | Blocking |
| Performance | Higher throughput | Lower throughput |
| Concurrency | Native async support | Thread-based |
| Resource Usage | More efficient | More memory per connection |
| Learning Curve | Async/await knowledge required | Simpler |
| Error Handling | Async exception handling | Standard exception handling |

## OpenTelemetry Integration

This sample can be enhanced with OpenTelemetry instrumentation:

```bash
# Run with OpenTelemetry instrumentation
opentelemetry-instrument python app.py
```

Set up tracing environment variables:
```bash
export OTEL_SERVICE_NAME="aio-pika-sample"
export OTEL_SERVICE_VERSION="1.0.0"
export OTEL_RESOURCE_ATTRIBUTES="service.name=aio-pika-sample,service.library=aio-pika"
```

## Learning Resources

- [aio-pika Documentation](https://aio-pika.readthedocs.io/)
- [RabbitMQ Documentation](https://www.rabbitmq.com/documentation.html)
- [Python asyncio Documentation](https://docs.python.org/3/library/asyncio.html)
- [AMQP 0.9.1 Specification](https://www.rabbitmq.com/amqp-0-9-1-reference.html)
- [Flask Documentation](https://flask.palletsprojects.com/)

## Clean Up

To stop all services and clean up:

```bash
# Stop services
docker-compose down

# Remove volumes (optional - deletes RabbitMQ data)
docker-compose down -v
```

## Advanced Usage

### Custom Exchanges with Async Operations
The sample uses the default exchange, but can be extended to use:
- Direct exchanges for routing by routing key (async)
- Topic exchanges for pattern-based routing (async)
- Fanout exchanges for broadcast messaging (async)

### Async Message Properties
Messages can include additional properties:
- Content type with async publishing
- Message expiration with async TTL
- Priority with async handling
- Custom headers with async processing

### Advanced Async Consumer Patterns
- Multiple async consumers on the same queue
- Consumer prefetch for async load balancing
- Manual acknowledgment with async error handling
- Consumer cancellation and graceful shutdown

### Event Loop Management
- Custom event loop policies
- Multiple event loops for different operations
- Async context managers for resource handling
- Proper async resource cleanup

## Performance Tips

1. **Use Batch Operations**: Leverage concurrent publishing for better throughput
2. **Optimize QoS Settings**: Adjust prefetch count based on consumer capacity
3. **Connection Pooling**: Use connection pooling for multiple operations
4. **Async Context Managers**: Properly manage async resources
5. **Monitor Event Loop**: Watch for event loop blocking operations
6. **Error Handling**: Implement proper async exception handling
