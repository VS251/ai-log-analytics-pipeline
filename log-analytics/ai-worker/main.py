import pika
import json
import time
import os
from elasticsearch import Elasticsearch
from transformers import pipeline, TFRobertaForSequenceClassification, RobertaTokenizer

print("--- AI Worker Starting ---")

try:
    print("Loading AI model...")
    sentiment_pipeline = pipeline(
        'sentiment-analysis', 
        model='distilbert-base-uncased-finetuned-sst-2-english'
    )
    print("AI model loaded successfully.")
except Exception as e:
    print(f"Error loading AI model: {e}")
    exit(1)


ELASTICSEARCH_HOST = os.getenv('ELASTICSEARCH_HOST', 'localhost')
es = None

while es is None:
    try:
        print(f"Connecting to Elasticsearch at {ELASTICSEARCH_HOST}...")
        es = Elasticsearch(
            [f"http://{ELASTICSEARCH_HOST}:9200"],
        )
        if not es.ping():
            raise ConnectionError("Elasticsearch ping failed")
        print("Connected to Elasticsearch successfully.")
    except Exception as e:
        print(f"Error connecting to Elasticsearch: {e}")
        print("Retrying in 5 seconds...")
        time.sleep(5)

RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'localhost')
connection = None

while connection is None:
    try:
        print(f"Connecting to RabbitMQ at {RABBITMQ_HOST}...")
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
        channel = connection.channel()
        channel.queue_declare(queue='log_queue', durable=True)
        print("Connected to RabbitMQ successfully.")
    except Exception as e:
        print(f"Error connecting to RabbitMQ: {e}")
        print("Retrying in 5 seconds...")
        time.sleep(5)


def callback(ch, method, properties, body):
    """
    This function is called every time a message is received
    from the 'log_queue'.
    """
    try:
        print("\n[Callback] Received new log.")
        
        log_data = json.loads(body.decode('utf-8'))
        log_message = log_data.get('message', '')

        if log_message:
            analysis = sentiment_pipeline(log_message)[0]
            log_data['ai_sentiment'] = analysis['label']
            log_data['ai_sentiment_score'] = analysis['score']
            print(f"[Callback] AI Analysis: {analysis['label']} ({analysis['score']:.2f})")
        else:
            print("[Callback] No 'message' field to analyze.")

        from datetime import datetime
        log_data['@timestamp'] = datetime.utcnow().isoformat()

        es.index(index="logs", document=log_data)
        print(f"[Callback] Enriched log saved to Elasticsearch.")

        ch.basic_ack(delivery_tag=method.delivery_tag)
        print(f"[Callback] Message acknowledged.")

    except Exception as e:
        print(f"[Callback] Error processing message: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)


print("\n[Main] Waiting for logs. To exit press CTRL+C")
channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='log_queue', on_message_callback=callback)

try:
    channel.start_consuming()
except KeyboardInterrupt:
    print("Shutting down worker...")
    connection.close()