import os
import time
from fastapi import FastAPI, HTTPException, Query 
from typing import Optional
from elasticsearch import Elasticsearch, NotFoundError
from fastapi.middleware.cors import CORSMiddleware

print("--- Query API Starting ---")

app = FastAPI()

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ELASTICSEARCH_HOST = os.getenv('ELASTICSEARCH_HOST', 'localhost')
es = None

while es is None:
    try:
        print(f"Connecting to Elasticsearch at {ELASTICSEARCH_HOST}...")
        es = Elasticsearch(
            [f"http://{ELASTICSEARCH_HOST}:9200"]
        )
        if not es.ping():
            raise ConnectionError("Elasticsearch ping failed")
        print("Connected to Elasticsearch successfully.")
    except Exception as e:
        print(f"Error connecting to Elasticsearch: {e}")
        print("Retrying in 5 seconds...")
        time.sleep(5)


@app.get("/")
def read_root():
    return {"status": "Query API is running!"}

@app.get("/api/logs")
def get_logs(search: Optional[str] = Query(None)): 
    """
    This is the main endpoint to fetch logs from Elasticsearch.
    It now accepts an optional 'search' query parameter.
    """
    try:
        if search:
            query = {
                "multi_match": {
                    "query": search,
                    "fields": ["message", "service", "level"] 
                }
            }
        else:
            query = {"match_all": {}}
        
            
        response = es.search(
            index="logs",
            query=query, 
            sort=[{"@timestamp": {"order": "desc"}}],
            size=50
        )
        
        hits = response['hits']['hits']
        logs = [hit['_source'] for hit in hits]
        
        return {"logs": logs}
    
    except NotFoundError:
        print("'logs' index not found. Returning empty list.")
        return {"logs": []}
    except Exception as e:
        print(f"Error querying Elasticsearch: {e}")
        raise HTTPException(status_code=500, detail="Error querying logs")