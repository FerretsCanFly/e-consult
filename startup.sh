#!/bin/bash

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Starting application..."
gunicorn --bind=0.0.0.0:8000 --worker-class uvicorn.workers.UvicornWorker --workers 2 --timeout 600 application:application