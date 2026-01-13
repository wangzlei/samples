#!/usr/bin/env python3
"""
Simple kafka-python application sample.

This is a basic Kafka producer/consumer app that demonstrates:
- Kafka message production using kafka-python
- Kafka message consumption using kafka-python
- OpenTelemetry instrumentation for Kafka

To run:
    1. Start Kafka with Docker:
       docker-compose up -d
    
    2. Install dependencies:
       pip install -r requirements.txt
    
    3. Run the app:
       python app.py

The app will produce and consume messages from a Kafka topic.
"""

import json
import logging
import threading
import time

from kafka import KafkaConsumer, KafkaProducer
from kafka.errors import KafkaError, KafkaTimeoutError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Kafka configuration
KAFKA_BOOTSTRAP_SERVERS = ["localhost:9092"]
TOPIC_NAME = "test-topic"


class KafkaPythonApp:
    def __init__(self):
        self.producer = None
        self.consumer = None
        self.running = False
        self.producer_thread = None
        self.consumer_thread = None

    def create_producer(self):
        """Create kafka-python producer."""
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                client_id="python-producer",
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                key_serializer=lambda k: k.encode("utf-8") if k else None,
                acks="all",  # Wait for all replicas to acknowledge
                retries=3,
                max_in_flight_requests_per_connection=1,
            )
            logger.info("kafka-python producer created successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to create kafka-python producer: {e}")
            return False

    def create_consumer(self):
        """Create kafka-python consumer."""
        try:
            self.consumer = KafkaConsumer(
                TOPIC_NAME,
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                client_id="python-consumer",
                group_id="test-group",
                auto_offset_reset="earliest",
                enable_auto_commit=True,
                value_deserializer=lambda m: json.loads(m.decode("utf-8")) if m else None,
                key_deserializer=lambda k: k.decode("utf-8") if k else None,
            )
            logger.info("kafka-python consumer created successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to create kafka-python consumer: {e}")
            return False

    def produce_messages(self):
        """Produce messages to Kafka topic."""
        if not self.producer:
            logger.error("Producer not initialized")
            return

        message_count = 0
        while self.running:
            try:
                message = {
                    "id": message_count,
                    "message": f"Hello from kafka-python producer - message {message_count}",
                    "timestamp": time.time(),
                }

                # Produce message
                future = self.producer.send(topic=TOPIC_NAME, key=f"key-{message_count}", value=message)

                # Wait for the message to be sent
                try:
                    record_metadata = future.get(timeout=10)
                    logger.info(
                        f"Produced message {message_count}: topic={record_metadata.topic}, "
                        f"partition={record_metadata.partition}, offset={record_metadata.offset}"
                    )
                except KafkaTimeoutError:
                    logger.error(f"Timeout producing message {message_count}")

                message_count += 1
                time.sleep(2)  # Send a message every 2 seconds

            except KafkaError as e:
                logger.error(f"Kafka error producing message: {e}")
            except Exception as e:
                logger.error(f"Unexpected error in producer: {e}")

        # Flush any remaining messages
        if self.producer:
            logger.info("Flushing remaining messages...")
            self.producer.flush()

    def consume_messages(self):
        """Consume messages from Kafka topic."""
        if not self.consumer:
            logger.error("Consumer not initialized")
            return

        logger.info(f"Starting to consume messages from topic: {TOPIC_NAME}")

        try:
            while self.running:
                try:
                    # Use a simple loop with timeout checking
                    message = None
                    start_time = time.time()
                    timeout = 1.0  # 1 second timeout

                    for msg in self.consumer:
                        message = msg
                        break

                    if message:
                        try:
                            logger.info(
                                f"Consumed message: key={message.key}, "
                                f"value={message.value}, partition={message.partition}, "
                                f"offset={message.offset}"
                            )

                            # Process the message
                            self.process_message(message.value)

                        except Exception as e:
                            logger.error(f"Error processing message: {e}")
                    else:
                        # No message received, sleep briefly
                        time.sleep(0.1)

                except Exception as e:
                    logger.error(f"Error in consumer loop: {e}")
                    time.sleep(1)

        except Exception as e:
            logger.error(f"Consumer error: {e}")
        finally:
            # Close consumer
            if self.consumer:
                self.consumer.close()

    def process_message(self, message):
        """Process consumed message."""
        logger.info(f"Processing message: {message}")
        # Add your message processing logic here
        pass

    def start(self):
        """Start the Kafka application."""
        logger.info("Starting kafka-python application...")

        # Initialize producer and consumer
        if not self.create_producer():
            logger.error("Failed to initialize producer")
            return

        if not self.create_consumer():
            logger.error("Failed to initialize consumer")
            return

        self.running = True

        # Start producer and consumer in separate threads
        try:
            self.producer_thread = threading.Thread(target=self.produce_messages)
            self.consumer_thread = threading.Thread(target=self.consume_messages)

            self.producer_thread.start()
            self.consumer_thread.start()

            # Wait for a short time to let some messages be produced and consumed
            time.sleep(30)  # Run for 30 seconds

        except KeyboardInterrupt:
            logger.info("Received interrupt signal, stopping...")
        finally:
            self.stop()

    def stop(self):
        """Stop the Kafka application."""
        logger.info("Stopping kafka-python application...")
        self.running = False

        # Wait for threads to finish
        if self.producer_thread and self.producer_thread.is_alive():
            self.producer_thread.join(timeout=5)

        if self.consumer_thread and self.consumer_thread.is_alive():
            self.consumer_thread.join(timeout=5)

        # Close producer and consumer
        if self.producer:
            self.producer.close()

        logger.info("Application stopped")


def wait_for_kafka():
    """Wait for Kafka to be available."""
    logger.info("Waiting for Kafka to be available...")
    max_retries = 30
    retry_count = 0

    while retry_count < max_retries:
        try:
            # Try to create a simple producer to test connectivity
            test_producer = KafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS, client_id="connectivity-test")

            # Get cluster metadata to ensure connection is working
            metadata = test_producer.partitions_for(TOPIC_NAME)
            test_producer.close()

            logger.info("Kafka is available!")
            return True

        except Exception as e:
            retry_count += 1
            logger.info(f"Kafka not ready (attempt {retry_count}/{max_retries}): {e}")
            time.sleep(2)

    logger.error("Kafka is not available after waiting")
    return False


if __name__ == "__main__":
    # Wait for Kafka to be ready
    if not wait_for_kafka():
        logger.error("Cannot connect to Kafka. Make sure Kafka is running.")
        exit(1)

    # Create and start the application
    app = KafkaPythonApp()
    try:
        app.start()
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.error(f"Application error: {e}")
    finally:
        app.stop()
        logger.info("Application stopped")
