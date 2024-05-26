from flask import Flask, jsonify
from prometheus_client import Summary, make_wsgi_app
from werkzeug.middleware.dispatcher import DispatcherMiddleware
import os
import signal
import sys

app = Flask(__name__)

REQUEST_TIME = Summary('request_processing_seconds', 'Time spent processing request')

instance = os.getenv('HOSTNAME', 'unknown')

@app.route('/')
@REQUEST_TIME.time()
def home():
    return f"Welcome to the Flask web server! Instance: {instance}"

@app.route('/status')
@REQUEST_TIME.time()
def status():
    server_info = {
        "status": "running",
        "server": "Flask",
        "version": "1.0",
        "instance": instance,
        "author": "Your Name"
    }
    return jsonify(server_info), 200

@app.route('/hello')
@REQUEST_TIME.time()
def hello():
    return f"Hello, this is a basic information page! Instance: {instance}"

app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    '/metrics': make_wsgi_app()
})

def handle_signal(sig, frame):
    print('Received signal to terminate. Shutting down gracefully...')
    sys.exit(0)

signal.signal(signal.SIGTERM, handle_signal)
signal.signal(signal.SIGINT, handle_signal)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)