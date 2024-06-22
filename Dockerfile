FROM python:3.11.9-alpine3.19

ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY ./requirements.txt /app
RUN pip install --no-cache-dir --upgrade -r requirements.txt
COPY ./src /app/src
COPY ./start.sh /app/start.sh
RUN chmod +x ./start.sh


ENV PYTHONPATH "${PYTHONPATH}:/app"
ENTRYPOINT ["sh", "./start.sh"]
