import pika
import json
import os
import time 
from fastapi import FastAPI, HTTPException, Response, status, Security, Request 
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
import uvicorn

class LogEntry(BaseModel):
    service: str
    level: str
    message: str

app = FastAPI()
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'rabbitmq')

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()

    response = await call_next(request)

    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)

    print(f"[{request.method}] {request.url.path} - {response.status_code} - {process_time:.4f}s")

    return response

@app.get("/")
def read_root():
    """ A simple endpoint to check if the API is alive. """
    return {"status": "Collector API is running!"}

@app.get("/health")
def health_check(response: Response):
    """
    Checks if the service is healthy and can connect to RabbitMQ.
    """
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
        if connection.is_open:
            connection.close()
            return {"status": "ok", "rabbitmq": "connected"}
    except Exception as e:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"status": "error", "rabbitmq": "disconnected", "detail": str(e)}

    response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return {"status": "error", "rabbitmq": "unknown"}

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

VALID_API_KEYS = ["my-secret-key-123"]

async def get_api_key(api_key_header: str = Security(api_key_header)):
    """Dependency to check for a valid API Key."""
    if api_key_header in VALID_API_KEYS:
        return api_key_header
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials"
        )

@app.post("/api/log")
def receive_log(log: LogEntry, api_key: str = Security(get_api_key)):
    """
    This function now connects, publishes, and disconnects
    for every single request. This is far more resilient.
    """
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
        channel = connection.channel()

        channel.queue_declare(queue='log_queue', durable=True)

        message_body = log.model_dump_json()

        channel.basic_publish(
            exchange='',
            routing_key='log_queue',
            body=message_body,
            properties=pika.BasicProperties(delivery_mode=2) 
        )

        connection.close()
        
        return {"status": "Log received and queued"}
    
    except pika.exceptions.AMQPConnectionError as e:
        print(f"ERROR: Could not connect to RabbitMQ: {e}")
        raise HTTPException(status_code=503, detail="RabbitMQ connection error")
    except Exception as e:
        print(f"ERROR: An unknown error occurred: {e}")
        raise HTTPException(status_code=500, detail="An error occurred")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)