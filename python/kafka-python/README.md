# Simple kafka-python Application Sample

This is a basic Kafka producer/consumer application that demonstrates:
- Kafka message production and consumption using kafka-python
- OpenTelemetry instrumentation for Kafka operations
- Docker-based Kafka setup with Confluent Platform
- Concurrent producer/consumer operations

## Features

- Kafka producer that sends messages every 2 seconds using kafka-python
- Kafka consumer that processes messages from the same topic
- Built-in connection health checks and retry logic
- Clean logging for monitoring message flow
- Docker Compose setup with Kafka, Zookeeper, and Kafka UI
- OpenTelemetry instrumentation for distributed tracing
- Proper delivery reports and error handling

## Architecture

- **Zookeeper**: Kafka cluster coordination
- **Kafka**: Message broker (Confluent Platform)
- **Kafka UI**: Web interface for monitoring topics and messages
- **Python App**: Producer/consumer application using kafka-python with OpenTelemetry

## Requirements

- Python 3.7+
- Docker and Docker Compose
- kafka-python library
- OpenTelemetry instrumentation packages

## Installation & Usage

### 1. Start Kafka Services

First, if you have any existing Kafka containers running, stop them:

```bash
# Optional: Stop any existing Kafka containers if needed
docker stop zookeeper kafka kafka-ui
docker rm zookeeper kafka kafka-ui
```

Start Kafka, Zookeeper, and Kafka UI using Docker Compose:

```bash
docker-compose up -d
```

This will start:
- Zookeeper on port 2181 (container: kafka-python-zookeeper)
- Kafka on port 9092 (container: kafka-python-broker)
- Kafka UI on port 8080 (container: kafka-python-ui)

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

kafka-python is a pure Python library, so no additional system dependencies are required.

### 3. Run the Application

```bash
python app.py
```

The application will:
1. Wait for Kafka to be available (up to 60 seconds)
2. Create a producer and consumer
3. Start producing messages every 2 seconds
4. Consume and process messages concurrently
5. Run for 30 seconds then stop gracefully

### 4. Monitor with Kafka UI

Open your browser and visit:
```
http://localhost:8080
```

You can monitor:
- Topics and partitions
- Message flow and offsets
- Consumer groups
- Broker health

## Configuration

### Kafka Settings
- **Bootstrap Servers**: `localhost:9092`
- **Topic Name**: `test-topic`
- **Consumer Group**: `test-group`
- **Auto Offset Reset**: `earliest`

### Message Format
```json
{
  "id": 0,
  "message": "Hello from kafka-python producer - message 0",
  "timestamp": 1640995200.123
}
```

## Docker Services

### Zookeeper
- **Image**: confluentinc/cp-zookeeper:7.4.0
- **Port**: 2181
- **Health Check**: Echo 'ruok' command

### Kafka
- **Image**: confluentinc/cp-kafka:7.4.0
- **Ports**: 9092 (client), 9101 (JMX)
- **Features**: Auto-create topics enabled
- **Health Check**: List topics command

### Kafka UI
- **Image**: provectuslabs/kafka-ui:latest
- **Port**: 8080
- **Features**: Topic management, message browsing, consumer monitoring

## OpenTelemetry Integration

The application uses OpenTelemetry instrumentation for Kafka operations, which automatically creates spans for:
- Kafka producer send operations
- Kafka consumer receive operations
- Message processing activities

Traces can be exported to observability platforms like:
- AWS X-Ray
- Jaeger
- Zipkin
- Other OpenTelemetry-compatible backends

## Development

### Running in Development Mode

For development, you can modify the application behavior:

1. **Change message frequency**: Modify the `time.sleep(2)` in the producer
2. **Add message processing logic**: Implement custom logic in `process_message()`
3. **Configure different topics**: Change `TOPIC_NAME` variable
4. **Adjust logging**: Modify the logging level in the configuration

### Stopping Services

Stop all Docker services:
```bash
docker-compose down
```

Remove volumes (clears all data):
```bash
docker-compose down -v
```

### Custom Configuration

You can customize Kafka settings by modifying environment variables in `docker-compose.yml`:

```yaml
environment:
  KAFKA_AUTO_CREATE_TOPICS_ENABLE: 'true'
  KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
  # Add more settings as needed
```

## Troubleshooting

### Common Issues

1. **Python 3.13 compatibility issue**:
   kafka-python library has a known compatibility issue with Python 3.13 due to missing vendored `six.moves` module.
   
   **Current Solutions to try (in order):**
   
   a) **Install with six dependency first**:
   ```bash
   pip install six==1.16.0
   pip install -r requirements.txt
   ```
   
   b) **Use Python 3.11 or 3.12** (recommended for now):
   ```bash
   pyenv install 3.12.0
   pyenv local 3.12.0
   pip install -r requirements.txt
   ```
   
   c) **Manual fix after installation**:
   If you still get the error, you may need to manually create the missing module:
   ```bash
   # Find your kafka installation
   python -c "import kafka; print(kafka.__file__)"
   # Then create the missing six.moves manually in the kafka/vendor directory
   ```
   
   **Alternative**: Use the confluent-kafka sample in `../confluence-kafka/` which has better Python 3.13 support.

2. **Kafka not available**: 
   - Check if Docker services are running: `docker-compose ps`
   - Wait longer for Kafka to initialize (can take 30-60 seconds)

3. **Port conflicts**:
   - Ensure ports 2181, 9092, and 8080 are not in use
   - Modify port mappings in docker-compose.yml if needed

4. **Connection timeouts**:
   - Increase the retry count in `wait_for_kafka()`
   - Check Docker container logs: `docker-compose logs kafka`

5. **Consumer timeout errors**:
   - kafka-python consumer uses `consumer_timeout_ms` for polling timeout
   - Adjust timeout values if needed for your use case

### Logs and Monitoring

Check application logs for message flow:
```bash
python app.py
```

Check Kafka container logs:
```bash
docker-compose logs -f kafka
```

Check all service logs:
```bash
docker-compose logs -f
```

## kafka-python vs confluent-kafka

This sample uses kafka-python, which is different from confluent-kafka:

### kafka-python
- Pure Python implementation
- Easier to install (no C dependencies)
- Good for development and simple use cases
- Synchronous and asynchronous API support
- Built-in serializers/deserializers

### confluent-kafka (used in ../confluence-kafka/)
- librdkafka-based (C library)
- Higher performance
- More production-ready features
- Better for high-throughput scenarios
- Requires system dependencies

Choose kafka-python for:
- Development and testing
- Simple applications
- Environments where installing C dependencies is difficult

Choose confluent-kafka for:
- Production applications
- High-throughput requirements
- Performance-critical scenarios

## Notes

This is a minimal Kafka application intended for demonstration purposes. It includes:
- Basic producer/consumer patterns using kafka-python
- Error handling and retries
- Health checks and graceful shutdown
- OpenTelemetry instrumentation setup

For production use, consider adding:
- Proper error handling and dead letter queues
- Message schemas and validation
- Security configuration (SSL/SASL)
- Monitoring and alerting
- Data persistence strategies
- Connection pooling and optimization
