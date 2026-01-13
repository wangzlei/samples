# Simple aiokafka Application Sample

This is a basic async Kafka producer/consumer application that demonstrates:
- Kafka message production and consumption using aiokafka
- OpenTelemetry instrumentation for Kafka operations
- Docker-based Kafka setup with Confluent Platform
- Async/await patterns for concurrent operations

## Features

- Async Kafka producer that sends messages every 2 seconds using aiokafka
- Async Kafka consumer that processes messages from the same topic
- Built-in connection health checks and retry logic with async operations
- Clean logging for monitoring message flow
- Docker Compose setup with Kafka, Zookeeper, and Kafka UI
- OpenTelemetry instrumentation for distributed tracing
- Proper delivery reports and error handling using async patterns

## Architecture

- **Zookeeper**: Kafka cluster coordination
- **Kafka**: Message broker (Confluent Platform)
- **Kafka UI**: Web interface for monitoring topics and messages
- **Python App**: Async producer/consumer application using aiokafka with OpenTelemetry

## Requirements

- Python 3.7+
- Docker and Docker Compose
- aiokafka library
- OpenTelemetry instrumentation packages

## Installation & Usage

### 1. Start Kafka Services

First, if you have any existing Kafka containers running, stop them:

```bash
# Optional: Stop any existing Kafka containers if needed
docker stop aiokafka-zookeeper aiokafka-broker aiokafka-ui
docker rm aiokafka-zookeeper aiokafka-broker aiokafka-ui
```

Start Kafka, Zookeeper, and Kafka UI using Docker Compose:

```bash
docker-compose up -d
```

This will start:
- Zookeeper on port 2182 (container: aiokafka-zookeeper)
- Kafka on port 9093 (container: aiokafka-broker)
- Kafka UI on port 8081 (container: aiokafka-ui)

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

aiokafka is built on top of kafka-python but provides async/await support for better concurrency.

### 3. Run the Application

```bash
python app.py
```

The application will:
1. Wait for Kafka to be available (up to 60 seconds) using async operations
2. Create async producer and consumer
3. Start producing messages every 2 seconds concurrently
4. Consume and process messages asynchronously
5. Run for 30 seconds then stop gracefully

### 4. Monitor with Kafka UI

Open your browser and visit:
```
http://localhost:8081
```

You can monitor:
- Topics and partitions
- Message flow and offsets
- Consumer groups
- Broker health

## Configuration

### Kafka Settings
- **Bootstrap Servers**: `localhost:9093` (note different port from kafka-python sample)
- **Topic Name**: `aiokafka-test-topic`
- **Consumer Group**: `aiokafka-test-group`
- **Auto Offset Reset**: `earliest`

### Message Format
```json
{
  "id": 0,
  "message": "Hello from aiokafka producer - message 0",
  "timestamp": 1640995200.123
}
```

## Docker Services

### Zookeeper
- **Image**: confluentinc/cp-zookeeper:7.4.0
- **Port**: 2182 (mapped to avoid conflicts with kafka-python sample)
- **Health Check**: Echo 'ruok' command

### Kafka
- **Image**: confluentinc/cp-kafka:7.4.0
- **Ports**: 9093 (client), 9102 (JMX)
- **Features**: Auto-create topics enabled
- **Health Check**: List topics command

### Kafka UI
- **Image**: provectuslabs/kafka-ui:latest
- **Port**: 8081 (mapped to avoid conflicts with kafka-python sample)
- **Features**: Topic management, message browsing, consumer monitoring

## aiokafka vs kafka-python

This sample uses aiokafka, which provides async/await support over kafka-python:

### aiokafka Advantages
- **Async/await support**: Natural integration with asyncio
- **Better concurrency**: Non-blocking I/O operations
- **Performance**: Better resource utilization for I/O-bound workloads
- **Modern Python**: Follows current async patterns

### Key Differences in Usage

**Producer Creation and Usage**:
```python
# aiokafka (async)
producer = AIOKafkaProducer(...)
await producer.start()
await producer.send_and_wait(topic, key, value)
await producer.stop()

# kafka-python (sync)
producer = KafkaProducer(...)
future = producer.send(topic, key, value)
record_metadata = future.get(timeout=10)
producer.close()
```

**Consumer Usage**:
```python
# aiokafka (async)
consumer = AIOKafkaConsumer(topic, ...)
await consumer.start()
async for message in consumer:
    await process_message(message.value)
await consumer.stop()

# kafka-python (sync)
consumer = KafkaConsumer(topic, ...)
for message in consumer:
    process_message(message.value)
consumer.close()
```

## OpenTelemetry Integration

The application uses OpenTelemetry instrumentation for Kafka operations, which automatically creates spans for:
- Async Kafka producer send operations
- Async Kafka consumer receive operations
- Async message processing activities

Traces can be exported to observability platforms like:
- AWS X-Ray
- Jaeger
- Zipkin
- Other OpenTelemetry-compatible backends

## Development

### Running in Development Mode

For development, you can modify the application behavior:

1. **Change message frequency**: Modify `await asyncio.sleep(2)` in the producer
2. **Add async message processing logic**: Implement custom async logic in `process_message()`
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

## Async Patterns in the Sample

### Concurrent Producer/Consumer
```python
async def start(self):
    # Start both producer and consumer concurrently
    producer_task = asyncio.create_task(self.produce_messages())
    consumer_task = asyncio.create_task(self.consume_messages())
    
    # Run for 30 seconds
    await asyncio.sleep(30)
```

### Async Message Processing
```python
async def process_message(self, message):
    """Process consumed message asynchronously."""
    logger.info(f"Processing message: {message}")
    # Simulate async processing (e.g., database operations, API calls)
    await asyncio.sleep(0.1)
```

### Async Connection Management
```python
async def create_producer(self):
    self.producer = AIOKafkaProducer(...)
    await self.producer.start()  # Async connection establishment
    
async def stop(self):
    if self.producer:
        await self.producer.stop()  # Async cleanup
```

## Troubleshooting

### Common Issues

1. **Port conflicts**: 
   - This sample uses ports 2182, 9093, and 8081 to avoid conflicts with kafka-python sample
   - Ensure these ports are not in use by other applications

2. **aiokafka installation issues**:
   - aiokafka requires kafka-python as a dependency
   - If you encounter issues, try: `pip install kafka-python aiokafka`

3. **Async context issues**:
   - Ensure you're running the main function with `asyncio.run(main())`
   - All Kafka operations must be awaited properly

4. **Connection timeouts with async operations**:
   - Increase timeout values in async connection attempts
   - Check that async operations are properly awaited

5. **Consumer not receiving messages**:
   - Verify the topic name matches between producer and consumer
   - Check that consumer group is properly configured
   - Ensure consumer is started before producer sends messages

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

## Performance Considerations

### aiokafka Benefits
- **Non-blocking I/O**: Better resource utilization
- **Concurrent operations**: Multiple async operations can run simultaneously
- **Memory efficiency**: Lower memory footprint for concurrent connections
- **Scalability**: Better suited for handling many concurrent connections

### When to Use aiokafka
- High-concurrency applications
- I/O-bound workloads
- Applications already using asyncio
- WebSocket or HTTP async servers that need Kafka integration
- Microservices with async frameworks (FastAPI, aiohttp, etc.)

### When to Use kafka-python
- Simple synchronous applications
- CPU-bound processing
- Traditional threading-based applications
- Simpler deployment requirements

## Integration with Async Frameworks

aiokafka integrates well with:
- **FastAPI**: Async web framework
- **aiohttp**: Async HTTP client/server
- **asyncpg**: Async PostgreSQL driver
- **aioredis**: Async Redis client

Example FastAPI integration:
```python
from fastapi import FastAPI
from aiokafka import AIOKafkaProducer

app = FastAPI()
producer = None

@app.on_event("startup")
async def startup_event():
    global producer
    producer = AIOKafkaProducer(...)
    await producer.start()

@app.post("/send-message")
async def send_message(message: dict):
    await producer.send_and_wait("topic", value=message)
    return {"status": "sent"}
```

## Notes

This is a minimal async Kafka application intended for demonstration purposes. It includes:
- Async producer/consumer patterns using aiokafka
- Proper async error handling and cleanup
- Async health checks and graceful shutdown
- OpenTelemetry instrumentation setup
- Concurrent async operations

For production use, consider adding:
- Proper async error handling and dead letter queues
- Message schemas and validation
- Security configuration (SSL/SASL)
- Async monitoring and alerting
- Connection pooling and optimization
- Backpressure handling in async consumers
- Circuit breakers for async operations
