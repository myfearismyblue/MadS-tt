#!/bin/sh

cd /app/src
alembic upgrade head
uvicorn --host 0.0.0.0 --port $1 --reload $2
