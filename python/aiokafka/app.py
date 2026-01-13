#!/usr/bin/env python3
"""
Simple aiokafka application sample.

This is a basic Kafka producer/consumer app that demonstrates:
- Kafka message production using aiokafka
- Kafka message consumption using aiokafka
- OpenTelemetry instrumentation for Kafka
- Async/await patterns

To run:
    1. Start Kafka with Docker:
       docker-compose up -d
    
    2. Install dependencies:
       pip install -r requirements.txt
    
    3. Run the app:
       python app.py

The app will produce and consume messages from a Kafka topic using async patterns.
"""

import asyncio
import json
import logging
import time

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from aiokafka.errors import KafkaError, KafkaTimeoutError

from opentelemetry.instrumentation.kafka import KafkaInstrumentor

# Instrument kafka (this also works for aiokafka)
KafkaInstrumentor().instrument()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Kafka configuration
KAFKA_BOOTSTRAP_SERVERS = ["localhost:9093"]
TOPIC_NAME = "aiokafka-test-topic"


class AioKafkaApp:
    def __init__(self):
        self.producer = None
        self.consumer = None
        self.running = False

    async def create_producer(self):
        """Create aiokafka producer."""
        try:
            self.producer = AIOKafkaProducer(
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                client_id="aiokafka-producer",
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                key_serializer=lambda k: k.encode("utf-8") if k else None,
                acks="all",  # Wait for all replicas to acknowledge
                request_timeout_ms=30000,  # 30 seconds timeout
                retry_backoff_ms=100,  # Backoff between retries
            )
            await self.producer.start()
            logger.info("aiokafka producer created and started successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to create aiokafka producer: {e}")
            return False

    async def create_consumer(self):
        """Create aiokafka consumer."""
        try:
            self.consumer = AIOKafkaConsumer(
                TOPIC_NAME,
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                client_id="aiokafka-consumer",
                group_id="aiokafka-test-group",
                auto_offset_reset="earliest",
                enable_auto_commit=True,
                value_deserializer=lambda m: json.loads(m.decode("utf-8")) if m else None,
                key_deserializer=lambda k: k.decode("utf-8") if k else None,
            )
            await self.consumer.start()
            logger.info("aiokafka consumer created and started successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to create aiokafka consumer: {e}")
            return False

    async def produce_messages(self):
        """Produce messages to Kafka topic."""
        if not self.producer:
            logger.error("Producer not initialized")
            return

        message_count = 0
        while self.running:
            try:
                message = {
                    "id": message_count,
                    "message": f"Hello from aiokafka producer - message {message_count}",
                    "timestamp": time.time(),
                }

                # Produce message
                try:
                    await self.producer.send_and_wait(topic=TOPIC_NAME, key=f"key-{message_count}", value=message)
                    logger.info(f"Produced message {message_count}: {message['message']}")
                except KafkaTimeoutError:
                    logger.error(f"Timeout producing message {message_count}")
                except KafkaError as e:
                    logger.error(f"Kafka error producing message {message_count}: {e}")

                message_count += 1
                await asyncio.sleep(2)  # Send a message every 2 seconds

            except Exception as e:
                logger.error(f"Unexpected error in producer: {e}")
                await asyncio.sleep(1)

    async def consume_messages(self):
        """Consume messages from Kafka topic."""
        if not self.consumer:
            logger.error("Consumer not initialized")
            return

        logger.info(f"Starting to consume messages from topic: {TOPIC_NAME}")

        try:
            async for message in self.consumer:
                if not self.running:
                    break

                try:
                    logger.info(
                        f"Consumed message: key={message.key}, "
                        f"value={message.value}, partition={message.partition}, "
                        f"offset={message.offset}"
                    )

                    # Process the message
                    await self.process_message(message.value)

                except Exception as e:
                    logger.error(f"Error processing message: {e}")

        except Exception as e:
            logger.error(f"Consumer error: {e}")

    async def process_message(self, message):
        """Process consumed message."""
        logger.info(f"Processing message: {message}")
        # Add your message processing logic here
        # Simulate some async processing
        await asyncio.sleep(0.1)

    async def start(self):
        """Start the aiokafka application."""
        logger.info("Starting aiokafka application...")

        # Initialize producer and consumer
        if not await self.create_producer():
            logger.error("Failed to initialize producer")
            return

        if not await self.create_consumer():
            logger.error("Failed to initialize consumer")
            return

        self.running = True

        # Start producer and consumer concurrently
        try:
            producer_task = asyncio.create_task(self.produce_messages())
            consumer_task = asyncio.create_task(self.consume_messages())

            # Wait for 30 seconds then stop
            await asyncio.sleep(30)

        except KeyboardInterrupt:
            logger.info("Received interrupt signal, stopping...")
        except Exception as e:
            logger.error(f"Application error: {e}")
        finally:
            await self.stop()

    async def stop(self):
        """Stop the aiokafka application."""
        logger.info("Stopping aiokafka application...")
        self.running = False

        # Stop producer and consumer
        if self.producer:
            try:
                await self.producer.stop()
                logger.info("Producer stopped")
            except Exception as e:
                logger.error(f"Error stopping producer: {e}")

        if self.consumer:
            try:
                await self.consumer.stop()
                logger.info("Consumer stopped")
            except Exception as e:
                logger.error(f"Error stopping consumer: {e}")

        logger.info("Application stopped")


async def wait_for_kafka():
    """Wait for Kafka to be available."""
    logger.info("Waiting for Kafka to be available...")
    max_retries = 30
    retry_count = 0

    while retry_count < max_retries:
        test_producer = None
        try:
            # Try to create a simple producer to test connectivity
            test_producer = AIOKafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS, client_id="connectivity-test")

            await test_producer.start()

            # Try to get cluster metadata to ensure connection is working
            # Use the producer's client to check metadata
            cluster = test_producer.client.cluster
            if cluster.brokers():
                logger.info("Kafka is available!")
                return True
            else:
                raise Exception("No brokers found in cluster")

        except Exception as e:
            retry_count += 1
            logger.info(f"Kafka not ready (attempt {retry_count}/{max_retries}): {e}")
            await asyncio.sleep(2)
        finally:
            # Ensure producer is properly closed
            if test_producer is not None:
                try:
                    await test_producer.stop()
                except Exception:
                    pass  # Ignore errors during cleanup

    logger.error("Kafka is not available after waiting")
    return False


async def main():
    # Wait for Kafka to be ready
    if not await wait_for_kafka():
        logger.error("Cannot connect to Kafka. Make sure Kafka is running.")
        return

    # Create and start the application
    app = AioKafkaApp()
    try:
        await app.start()
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.error(f"Application error: {e}")
    finally:
        await app.stop()
        logger.info("Application stopped")


if __name__ == "__main__":
    asyncio.run(main())
