# 🤖 AI-Powered Log Analytics Pipeline

A complete, end-to-end log ingestion and analytics platform built with a real-time, microservices-based architecture. This system collects logs, processes them with an AI model for sentiment analysis, and displays them on a live, interactive dashboard.

### ✨ Key Features

* **Asynchronous Ingestion:** A high-throughput FastAPI collector API accepts logs and pushes them to a RabbitMQ queue.
* **AI Processing:** A Python worker consumes logs, analyzes their sentiment using a Hugging Face model, and enriches them.
* **Real-Time Analytics:** All enriched logs are stored and indexed in Elasticsearch for high-speed search.
* **Interactive Dashboard:** A React frontend provides a live view of all logs, with real-time charts and filtering capabilities.
* **Containerized:** The entire backend is fully containerized with Docker and managed by Docker Compose for one-command startup.

---

### 🏛️ System Architecture

This project uses a decoupled, event-driven architecture to ensure scalability and resilience.

D**Data Ingestion (Write Path):** [Dummy App / curl] -> [Collector API (FastAPI)] -> [RabbitMQ Queue] -> [AI Worker (Python)] -> [Elasticsearch]

**Data Visualization (Read Path):** [React Dashboard] -> [Query API (FastAPI)] -> [Elasticsearch]


---

### 🚀 Tech Stack

| Area | Technology | Purpose |
| :--- | :--- | :--- |
| **Backend** | Python, FastAPI | For building the `collector-api` and `query-api`. |
| **Database** | Elasticsearch | Main datastore for log storage, search, and analytics. |
| **Message Broker**| RabbitMQ | Decouples the ingestion API from the processing worker. |
| **AI / ML** | Hugging Face `transformers` | For on-the-fly, self-hosted sentiment analysis. |
| **Frontend** | React, Recharts | For the interactive dashboard and visualizations. |
| **DevOps** | Docker, Docker Compose | To containerize and run the entire backend system. |
| **Simulator** | Python (`requests`) | To generate a realistic, constant stream of log data. |

---

### 🏁 How to Run

You only need **Node.js** and **Docker Desktop** installed.

```bash

#### 1. Run the Backend

The entire backend (all 4 services) runs with one command:

# 1. Clone this repository
git clone [https://github.com/YOUR_USERNAME/ai-log-analytics-pipeline.git](https://github.com/YOUR_USERNAME/ai-log-analytics-pipeline.git)
cd ai-log-analytics-pipeline/log-analytics

# 2. Build and run the containers
docker-compose up -d --build

#### 2. Run the Frontend Dashboard

# 1. In a new terminal, navigate to the dashboard
cd ../log-dashboard

# 2. Install dependencies and start
npm install
npm start

Your dashboard is now live at http://localhost:3000.

#### 3. (Optional) Run the Data Simulator

# 1. In another new terminal, navigate to the dummy app
cd ../dummy-app

# 2. Install dependencies and run
pip3 install requests
python3 app.py

Watch your dashboard come alive with data!