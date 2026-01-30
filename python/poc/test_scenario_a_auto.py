"""
Scenario A Test: Simple Flask Application for Manual Testing

This is a minimal Flask application to test opentelemetry-instrument auto-instrumentation
with managed monitoring injection.

Usage:
    OTEL_TRACES_EXPORTER=console OTEL_METRICS_EXPORTER=none \
        opentelemetry-instrument python test_scenario_a_auto.py

Then visit:
    http://localhost:5000/
    http://localhost:5000/api/users
    http://localhost:5000/api/data

You should see detailed span exports from ManagedExporter in the console.
"""

from flask import Flask, jsonify
import time

app = Flask(__name__)


@app.route('/')
def home():
    """Simple home endpoint"""
    return jsonify({
        'message': 'Welcome to Scenario A Test',
        'endpoints': [
            '/',
            '/api/users',
            '/api/data'
        ]
    })


@app.route('/api/users')
def get_users():
    """Simulate fetching users with some processing time"""
    time.sleep(0.05)  # Simulate database query
    return jsonify({
        'users': [
            {'id': 1, 'name': 'Alice'},
            {'id': 2, 'name': 'Bob'},
            {'id': 3, 'name': 'Charlie'}
        ]
    })


@app.route('/api/data')
def get_data():
    """Simulate fetching data with some processing time"""
    time.sleep(0.03)  # Simulate API call
    return jsonify({
        'data': {
            'timestamp': time.time(),
            'value': 42
        }
    })


if __name__ == '__main__':
    print('=' * 70)
    print('Scenario A Test - Flask Application')
    print('=' * 70)
    print('')
    print('Application is running at: http://localhost:5000')
    print('')
    print('Available endpoints:')
    print('  GET  http://localhost:5000/')
    print('  GET  http://localhost:5000/api/users')
    print('  GET  http://localhost:5000/api/data')
    print('')
    print('What to look for:')
    print('  1. [ManagedInformer] logs showing successful injection')
    print('  2. [ManagedExporter] logs showing detailed span exports')
    print('  3. Console exporter output (if OTEL_TRACES_EXPORTER=console)')
    print('')
    print('Press Ctrl+C to stop')
    print('=' * 70)
    print('')
    
    app.run(host='0.0.0.0', port=5000, debug=False)
