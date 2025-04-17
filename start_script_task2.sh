#!/bin/bash

echo "Starting db service..."
uvicorn db_service:app --host 0.0.0.0 --port 9000 &

echo "Starting business logic service..."
uvicorn business_service:app --host 0.0.0.0 --port 8001 &

wait

echo "All services started"