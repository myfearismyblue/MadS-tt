#!/bin/sh

cd /app/src
alembic upgrade head
uvicorn --host 0.0.0.0 --port $WEB_APP_PORT --reload src.public.app:app
