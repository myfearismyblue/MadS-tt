#!/bin/sh

uvicorn --host 0.0.0.0 --port $APP_PORT --reload src.app:app
