#!/bin/bash

cd app
echo "Starting db service..."
uvicorn db_service:app --host 127.0.0.1 --port 9000 &

echo "Starting business logic service..."
uvicorn business_service:app --host 127.0.0.1 --port 8001 &

echo "Starting client service..."
uvicorn client_service:app --host 127.0.0.1 --port 8000 &

wait

echo "All services started"
