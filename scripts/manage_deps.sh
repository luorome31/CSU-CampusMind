#!/bin/bash

# CampusMind External Dependencies Manager
# This script manages the external dependencies (PostgreSQL, MinIO, Elasticsearch) using Docker.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPOSE_FILE="$SCRIPT_DIR/docker-compose-deps.yml"

usage() {
    echo "Usage: $0 {start|stop|restart|status|logs}"
    exit 1
}

if [ -z "$1" ]; then
    usage
fi

case "$1" in
    start)
        echo "Starting external dependencies..."
        docker compose -f "$COMPOSE_FILE" up -d
        ;;
    stop)
        echo "Stopping external dependencies..."
        docker compose -f "$COMPOSE_FILE" down
        ;;
    restart)
        echo "Restarting external dependencies..."
        docker compose -f "$COMPOSE_FILE" restart
        ;;
    status)
        docker compose -f "$COMPOSE_FILE" ps
        ;;
    logs)
        docker compose -f "$COMPOSE_FILE" logs -f
        ;;
    *)
        usage
        ;;
esac
