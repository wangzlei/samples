# Celery Sample Application

This sample demonstrates how to use Celery, a distributed task queue system, with Redis as the message broker. The application showcases various Celery features including basic task execution, long-running tasks with progress tracking, task chaining, error handling, and retries.

## Features Demonstrated

- **Basic Task Execution**: Simple mathematical operations (add, multiply)
- **Long-Running Tasks**: Tasks with progress tracking and status updates
- **Task Chaining**: Sequential execution of multiple tasks
- **Task Groups and Chords**: Parallel execution with result aggregation
- **Error Handling**: Automatic retry mechanisms for failing tasks
- **Task Monitoring**: Real-time status tracking and result retrieval
- **Web Interface**: Flask-based UI for triggering and monitoring tasks

## Prerequisites

- Python 3.7+
- Docker and Docker Compose (for Redis)
- pip for installing Python dependencies

## Setup and Installation

1. **Navigate to the celery sample directory:**
   ```bash
   cd samples/celery
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start Redis using Docker Compose:**
   ```bash
   docker-compose up -d
   ```
   
   This will start:
   - Redis server on port 6379
   - Redis Commander (web UI) on port 8081

4. **Verify Redis is running:**
   ```bash
   docker-compose ps
   ```

## Running the Application

The Celery sample consists of three components that need to be started in separate terminals:

### Terminal 1: Start the Celery Worker

```bash
cd samples/celery
celery -A celery_app worker --loglevel=info
```

The worker will display available tasks and start processing jobs from the queue.

### Terminal 2: Start the Flask Web Application

```bash
cd samples/celery
python app.py
```

The Flask app will start on http://localhost:5000

### Terminal 3: (Optional) Start Celery Flower for Monitoring

Install and start Flower for advanced monitoring:

```bash
pip install flower
celery -A celery_app flower
```

Flower will be available at http://localhost:5555

## Using the Application

1. **Open the Web Interface**: Visit http://localhost:5000 in your browser

2. **Execute Basic Tasks**: Try the math operations (add/multiply) with different numbers

3. **Run Long Tasks**: Start a long-running task and watch the progress updates

4. **Test Task Chaining**: Execute a chain of tasks to see sequential processing

5. **Data Workflows**: Generate random data and process it using task coordination

6. **Error Handling**: Run the failing task to see retry behavior

7. **Monitor Tasks**: Use the task status checker to monitor any task by ID

## Additional Monitoring Tools

- **Redis Commander**: http://localhost:8081 - View Redis data and queues
- **Celery Flower**: http://localhost:5555 - Advanced task monitoring (if installed)
- **Worker Logs**: Check the terminal running the Celery worker for detailed logs

## Task Types

### Basic Tasks
- `add_numbers(x, y)`: Adds two numbers
- `multiply_numbers(x, y)`: Multiplies two numbers

### Advanced Tasks
- `long_running_task(duration)`: Simulates work with progress updates
- `generate_random_data(count)`: Generates random data points
- `process_data(data)`: Calculates statistics from data
- `chain_example(x)`: Task designed for chaining (squares input + 10)
- `failing_task()`: Demonstrates retry behavior

### Task Patterns
- **Chains**: Sequential execution of tasks
- **Groups**: Parallel execution of multiple tasks
- **Chords**: Parallel execution with result aggregation
- **Retries**: Automatic retry on failure with exponential backoff

## Configuration

The Celery configuration is in `celery_app.py`:

- **Broker URL**: `redis://localhost:6379/0`
- **Result Backend**: `redis://localhost:6379/0`
- **Serializer**: JSON
- **Task Expiration**: 1 hour
- **Timezone**: UTC

## Troubleshooting

### Common Issues

1. **Redis Connection Error**:
   - Ensure Redis is running: `docker-compose ps`
   - Check Redis logs: `docker-compose logs redis`

2. **No Workers Available**:
   - Make sure the Celery worker is running
   - Check worker logs for errors

3. **Tasks Not Executing**:
   - Verify task registration in worker startup logs
   - Check Redis queue status in Redis Commander

4. **Import Errors**:
   - Ensure all dependencies are installed: `pip install -r requirements.txt`
   - Check Python path and module imports

### Useful Commands

```bash
# Check Redis status
docker-compose ps

# View Redis logs
docker-compose logs redis

# Check Celery worker status
celery -A celery_app inspect active

# View task registrations
celery -A celery_app inspect registered

# Purge all tasks from queue
celery -A celery_app purge

# Stop all services
docker-compose down
```

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Flask App     │    │   Redis Broker  │    │  Celery Worker  │
│   (Web UI)      │────│   (Message      │────│   (Task         │
│   Port 5000     │    │    Queue)       │    │   Processor)    │
│                 │    │   Port 6379     │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐              │
         └──────────────│   Task Results  │──────────────┘
                        │   (Redis DB)    │
                        └─────────────────┘
```

## Learning Resources

- [Celery Documentation](https://docs.celeryproject.org/)
- [Redis Documentation](https://redis.io/documentation)
- [Flask Documentation](https://flask.palletsprojects.com/)

## Clean Up

To stop all services and clean up:

```bash
# Stop services
docker-compose down

# Remove volumes (optional - deletes Redis data)
docker-compose down -v
