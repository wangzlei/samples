#!/usr/bin/env python3
"""
Simple Confluent-Kafka application sample.

This is a basic Kafka producer/consumer app that demonstrates:
- Kafka message production using confluent-kafka
- Kafka message consumption using confluent-kafka
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

from confluent_kafka import Consumer, KafkaError, KafkaException, Producer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Kafka configuration
KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"
TOPIC_NAME = "test-topic"


class ConfluentKafkaApp:
    def __init__(self):
        self.producer = None
        self.consumer = None
        self.running = False
        self.producer_thread = None
        self.consumer_thread = None

    def create_producer(self):
        """Create Confluent Kafka producer."""
        try:
            producer_config = {"bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS, "client.id": "python-producer"}
            self.producer = Producer(producer_config)
            logger.info("Confluent Kafka producer created successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to create Confluent Kafka producer: {e}")
            return False

    def create_consumer(self):
        """Create Confluent Kafka consumer."""
        try:
            consumer_config = {
                "bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS,
                "group.id": "test-group",
                "auto.offset.reset": "earliest",
                "client.id": "python-consumer",
            }
            self.consumer = Consumer(consumer_config)
            self.consumer.subscribe([TOPIC_NAME])
            logger.info("Confluent Kafka consumer created successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to create Confluent Kafka consumer: {e}")
            return False

    def delivery_report(self, err, msg):
        """Delivery report callback for producer."""
        if err is not None:
            logger.error(f"Message delivery failed: {err}")
        else:
            logger.info(f"Message delivered to topic {msg.topic()} partition {msg.partition()} offset {msg.offset()}")

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
                    "message": f"Hello from Confluent Kafka producer - message {message_count}",
                    "timestamp": time.time(),
                }

                # Produce message
                self.producer.produce(
                    topic=TOPIC_NAME,
                    key=f"key-{message_count}",
                    value=json.dumps(message),
                    callback=self.delivery_report,
                )

                # Trigger delivery report callbacks
                self.producer.poll(0)

                logger.info(f"Produced message {message_count}: {message}")
                message_count += 1
                time.sleep(2)  # Send a message every 2 seconds

            except KafkaException as e:
                logger.error(f"Kafka error producing message: {e}")
            except Exception as e:
                logger.error(f"Unexpected error in producer: {e}")

        # Wait for any outstanding messages to be delivered
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
                msg = self.consumer.poll(timeout=1.0)

                if msg is None:
                    continue

                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        # End of partition event
                        logger.info(
                            f"End of partition reached {msg.topic()} [{msg.partition()}] at offset {msg.offset()}"
                        )
                    elif msg.error():
                        logger.error(f"Consumer error: {msg.error()}")
                        break
                else:
                    # Proper message
                    try:
                        message_value = json.loads(msg.value().decode("utf-8"))
                        logger.info(
                            f"Consumed message: key={msg.key().decode('utf-8') if msg.key() else None}, "
                            f"value={message_value}, partition={msg.partition()}, offset={msg.offset()}"
                        )

                        # Process the message
                        self.process_message(message_value)

                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to decode message JSON: {e}")
                    except Exception as e:
                        logger.error(f"Error processing message: {e}")

        except KafkaException as e:
            logger.error(f"Consumer error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in consumer: {e}")
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
        logger.info("Starting Confluent-Kafka application...")

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
        logger.info("Stopping Confluent-Kafka application...")
        self.running = False

        # Wait for threads to finish
        if self.producer_thread and self.producer_thread.is_alive():
            self.producer_thread.join(timeout=5)

        if self.consumer_thread and self.consumer_thread.is_alive():
            self.consumer_thread.join(timeout=5)

        logger.info("Application stopped")


def wait_for_kafka():
    """Wait for Kafka to be available."""
    logger.info("Waiting for Kafka to be available...")
    max_retries = 30
    retry_count = 0

    while retry_count < max_retries:
        try:
            # Try to create a simple producer to test connectivity
            test_config = {"bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS, "client.id": "connectivity-test"}
            test_producer = Producer(test_config)

            # Get metadata to ensure connection is working
            metadata = test_producer.list_topics(timeout=5)
            test_producer.flush()

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
    app = ConfluentKafkaApp()
    try:
        app.start()
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.error(f"Application error: {e}")
    finally:
        app.stop()
        logger.info("Application stopped")
