# Pika (RabbitMQ) Sample Application

This sample demonstrates how to use Pika, the Python client for RabbitMQ message broker. The application showcases various RabbitMQ messaging patterns including message publishing, consuming, queue management, and connection handling through a web interface.

## Features Demonstrated

- **Message Publishing**: Send individual messages or batches to RabbitMQ queues
- **Message Consuming**: Real-time message consumption with automatic acknowledgment
- **Queue Management**: Create queues and monitor queue statistics
- **Connection Management**: Connect/disconnect to RabbitMQ with status monitoring
- **Web Interface**: Flask-based UI for interacting with RabbitMQ
- **Real-time Updates**: Auto-refreshing message display
- **Error Handling**: Proper connection and error management

## Prerequisites

- Python 3.7+
- Docker and Docker Compose (for RabbitMQ)
- pip for installing Python dependencies

## Setup and Installation

1. **Navigate to the pika sample directory:**
   ```bash
   cd samples/pika
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
cd samples/pika
python app.py
```

The Flask app will start on http://localhost:5000

## Using the Application

1. **Open the Web Interface**: Visit http://localhost:5000 in your browser

2. **Connect to RabbitMQ**: Click "Connect to RabbitMQ" to establish connection

3. **Create Queues**: Use the Queue Management section to create new queues

4. **Publish Messages**: 
   - Send individual messages with custom content
   - Publish multiple messages in batch

5. **Start Consumer**: Begin consuming messages from a queue to see real-time message processing

6. **Monitor Activity**: 
   - View received messages in real-time
   - Check queue information (message count, consumer count)
   - Monitor connection status

## Application Sections

### Connection Management
- Connect/disconnect to RabbitMQ
- Check connection status
- View connection information

### Queue Management
- Create durable queues
- Get queue information (message count, consumer count)
- Monitor queue statistics

### Message Publishing
- Publish individual messages with custom content
- Batch publish multiple messages
- JSON message format support

### Consumer Management
- Start/stop message consumers
- Real-time message processing
- Automatic message acknowledgment

### Message Monitoring
- View received messages in real-time
- Auto-refresh every 2 seconds
- Clear message history

## Additional Monitoring Tools

- **RabbitMQ Management UI**: http://localhost:15672 (guest/guest)
  - View queues, exchanges, and connections
  - Monitor message rates and statistics
  - Manage RabbitMQ configuration

## Message Flow

1. **Publishing**: Messages are sent to named queues with persistence enabled
2. **Queuing**: RabbitMQ stores messages in durable queues
3. **Consuming**: Consumer threads process messages and acknowledge them
4. **Monitoring**: Web interface displays real-time message activity

## Configuration

The RabbitMQ configuration in the application:

- **Host**: localhost
- **Port**: 5672
- **Connection Parameters**:
  - Heartbeat: 600 seconds
  - Blocked connection timeout: 300 seconds
- **Queue Settings**: Durable queues for message persistence
- **Message Properties**: Persistent messages (delivery_mode=2)

## Troubleshooting

### Common Issues

1. **RabbitMQ Connection Error**:
   - Ensure RabbitMQ is running: `docker-compose ps`
   - Check RabbitMQ logs: `docker-compose logs rabbitmq`
   - Verify port 5672 is not blocked

2. **Consumer Not Receiving Messages**:
   - Make sure consumer is started
   - Check if messages are being published to the correct queue
   - Verify queue exists and has messages

3. **Web Interface Issues**:
   - Ensure Flask app is running on port 5000
   - Check browser console for JavaScript errors
   - Try refreshing the page

4. **Import Errors**:
   - Ensure all dependencies are installed: `pip install -r requirements.txt`
   - Check Python version compatibility

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
docker exec -it pika-sample-rabbitmq bash

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
│   Flask App     │    │   RabbitMQ      │    │   Consumer      │
│   (Web UI)      │────│   (Message      │────│   (Background   │
│   Port 5000     │    │    Broker)      │    │    Thread)      │
│                 │    │   Port 5672     │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐              │
         └──────────────│  Management UI  │──────────────┘
                        │   Port 15672    │
                        └─────────────────┘
```

## Message Patterns

### Basic Queue Pattern
- Producer sends messages to a named queue
- Consumer processes messages from the queue
- Messages are acknowledged after processing

### Batch Processing
- Multiple messages published in sequence
- Consumer processes each message individually
- Automatic acknowledgment ensures message delivery

## OpenTelemetry Integration

This sample can be enhanced with OpenTelemetry instrumentation:

```bash
# Run with OpenTelemetry instrumentation
opentelemetry-instrument python app.py
```

Set up tracing environment variables:
```bash
export OTEL_SERVICE_NAME="pika-sample"
export OTEL_SERVICE_VERSION="1.0.0"
export OTEL_RESOURCE_ATTRIBUTES="service.name=pika-sample"
```

## Learning Resources

- [Pika Documentation](https://pika.readthedocs.io/)
- [RabbitMQ Documentation](https://www.rabbitmq.com/documentation.html)
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

### Custom Exchanges
The sample uses the default exchange, but can be extended to use:
- Direct exchanges for routing by routing key
- Topic exchanges for pattern-based routing
- Fanout exchanges for broadcast messaging

### Message Properties
Messages can include additional properties:
- Content type
- Message expiration
- Priority
- Custom headers

### Consumer Patterns
- Multiple consumers on the same queue (work queue pattern)
- Consumer prefetch for load balancing
- Manual acknowledgment for error handling
