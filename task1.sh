# !bin/bash

podman machine start
podman build -t task1 .
podman run -p 8000:8000 task1