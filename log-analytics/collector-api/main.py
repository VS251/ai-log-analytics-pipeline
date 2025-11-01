import pika
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import os

class LogEntry(BaseModel):
    service: str
    level: str
    message: str

app = FastAPI()
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'rabbitmq')

@app.get("/")
def read_root():
    """ A simple endpoint to check if the API is alive. """
    return {"status": "Collector API is running!"}


@app.post("/api/log")
def receive_log(log: LogEntry):
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