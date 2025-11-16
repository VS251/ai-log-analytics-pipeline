import requests
import time
import random

print("--- Dummy Log Sender ---")
print("Starting in 3 seconds... (Press CTRL+C to stop)")
time.sleep(3)

services = ["payment-api", "user-service", "order-service", "frontend-web", "recommendation-engine"]
levels = ["INFO", "INFO", "INFO", "WARN", "ERROR", "DEBUG"] 
messages = [
    "User login successful for user_id: 123",
    "Payment processed successfully. OrderID: 456",
    "New user registered: varun@example.com",
    "Order 789 shipped.",
    "Data export job complete.",
    "Payment failed: Invalid CVC.",
    "Database connection timeout.",
    "User authentication failed: Bad credentials.",
    "NullPointerException in processOrder()",
    "API gateway returned 503 Service Unavailable."
]

API_URL = "http://localhost:8000/api/log"

while True:
    try:
        log_entry = {
            "service": random.choice(services),
            "level": random.choice(levels),
            "message": random.choice(messages)
        } 

        headers = {"X-API-Key": "my-secret-key-123"}
        
        response = requests.post(API_URL, json=log_entry, headers=headers, timeout=5)

        if response.status_code == 200:
            print(f"Sent log: {log_entry['level']} - {log_entry['message']}")
        else:
            print(f"Failed to send log. Status: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print(f"ERROR: Could not connect to {API_URL}. Is the Collector API running?")
    except Exception as e:
        print(f"An unknown error occurred: {e}")

    time_to_sleep = random.uniform(0.5, 3.0) 
    time.sleep(time_to_sleep)