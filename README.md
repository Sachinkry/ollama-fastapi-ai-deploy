# Prodify AI Inference Gateway

## A Scalable and Robust Asynchronous AI Inference System

This project demonstrates a modern, scalable, and fault-tolerant architecture for serving AI model inferences asynchronously. It's designed to handle concurrent requests efficiently, provide real-time status updates, and integrate seamlessly with various Large Language Models (LLMs) via Ollama.

## Key Features & Benefits

- **Asynchronous Inference:** Leverages Celery and Redis for background task processing, ensuring a responsive user experience and efficient resource utilization.
- **Scalable Architecture:** Built with FastAPI, Celery, and Redis, the system can easily scale horizontally to meet increasing demand for AI inferences.
- **LLM Agnostic:** Integrates with Ollama, allowing for flexible deployment and experimentation with various local Large Language Models (LLMs) like Qwen and Mistral.
- **Modern Frontend:** A responsive and interactive user interface developed with React (Vite + Shadcn) for seamless user interaction and real-time feedback.
- **Secure API Access:** Implements API key-based authentication to secure inference endpoints.
- **Observability:** Includes Prometheus metrics for monitoring system performance and health.
- **Containerized Deployment:** Docker and Docker Compose configurations for easy setup, deployment, and environment consistency.

## Architecture Overview

The system is composed of several interconnected services, each playing a crucial role in the inference pipeline:

```
+-------------------+       +-------------------+       +-------------------+
| Frontend (React)  | <---> | FastAPI Gateway   | <---> | Redis (Broker)    |
| (User Interface)  |       | (API, Auth, Queue)|       | (Task Queue)      |
+-------------------+       +-------------------+       +-------------------+
         ▲                           │                           │
         │                           │                           ▼
         │                     (Enqueues Task)             +-------------------+
         │                                                 | Celery Worker     |
         │                                                 | (Task Execution)  |
         │                                                 +-------------------+
         │                                                           │
         │                                                           ▼
         │                                                     +-------------------+
         +-----------------------------------------------------| Ollama (LLM)      |
           (Polls for Results)                                 | (Model Inference) |
                                                               +-------------------+
```

### Component Breakdown:

- **Frontend (React + Shadcn):** A single-page application (SPA) built with React, Vite, and Shadcn UI components. It provides an intuitive interface for users to submit prompts, select LLMs, and view inference results in real-time through polling.
- **FastAPI Gateway:** The central API layer built with FastAPI. It handles:
  - API key authentication.
  - Routing for inference requests (`/generate`), model listing (`/models`), and status checks (`/status/{job_id}`).
  - Enqueuing inference tasks to Celery.
  - Exposing Prometheus metrics for monitoring.
- **Redis:** Serves as both the message broker for Celery (managing the task queue) and the backend for storing Celery task results.
- **Celery Worker:** A distributed task queue worker that consumes tasks from Redis. It orchestrates the actual LLM inference by interacting with the Ollama service.
- **Ollama:** A powerful tool for running Large Language Models locally. The Celery worker sends prompts to Ollama, which then performs the inference using the selected LLM (e.g., Qwen, Mistral).

## Tech Stack

| Layer                | Technology                         | Role                                                             |
| :------------------- | :--------------------------------- | :--------------------------------------------------------------- |
| **Frontend**         | React, Vite, Shadcn UI, TypeScript | Interactive UI for prompt submission and result display          |
| **Backend API**      | FastAPI, Python                    | High-performance API gateway, authentication, task enqueuing     |
| **Task Queue**       | Celery, Redis                      | Asynchronous task management, message brokering, result storage  |
| **LLM Inference**    | Ollama                             | Local LLM serving (supports various models like Qwen, Mistral)   |
| **Containerization** | Docker, Docker Compose             | Environment consistency, simplified deployment and orchestration |
| **Monitoring**       | Prometheus Client (Python)         | Capturing and exposing application metrics                       |

## Project Structure

```
.github/             # GitHub Actions workflows
app/                 # FastAPI backend application code
├── api/             # API routes (generate, models, status)
├── core/            # Core configurations, auth, logging, metrics
├── models/          # LLM model definitions and registry
├── schemas/         # Pydantic schemas for data validation
├── services/        # External service integrations (e.g., OllamaClient)
├── static/          # Static files for the frontend
└── worker.py        # Celery worker tasks
frontend/            # React frontend application code
├── public/          # Public assets
├── src/             # React source code
└── Dockerfile.frontend # Dockerfile for the frontend Nginx server
tests/               # Unit and integration tests
.env.example         # Example environment variables
docker-compose.yml   # Docker Compose configuration
Dockerfile           # Dockerfile for the FastAPI backend and Celery worker
README.md            # Project README
repomix-output.xml   # LLM-friendly repository overview
requirements.txt     # Python dependencies
```

## LLM-Friendly Repository Overview

This repository includes a `repomix-output.xml` file, which provides an LLM-friendly, structured overview of the entire codebase. This file can be used by large language models or other automated tools to quickly understand the project's structure, components, and relationships, facilitating code analysis, documentation generation, and automated development tasks.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

- Docker and Docker Compose
- Git

### Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/sachinkumaryadav/deploy-ai-fastapi.git
    cd deploy-ai-fastapi
    ```

2.  **Configure Environment Variables:**
    Copy the example environment file and update it with your API keys.

    ```bash
    cp .env.example .env
    # Open .env and set your API_KEYS (e.g., API_KEYS="dev-key-123,prod-key-456")
    ```

3.  **Start the Services:**
    Use Docker Compose to build and run all services. This will start Redis, Ollama, FastAPI backend, Celery worker, and the Nginx frontend.

    ```bash
    docker-compose up --build -d
    ```

    _Note: The first time you run this, Ollama will download the specified LLM models, which might take some time depending on your internet connection and the model sizes._

4.  **Access the Application:**
    - **Frontend:** Open your web browser and navigate to `http://localhost:8080`
    - **FastAPI Backend:** The API will be available at `http://localhost:8000`

### Usage

1.  **Select a Model:** On the frontend, choose an available LLM. The application will list models that Ollama has loaded. If no models are listed, you may need to pull them manually (see note below).
2.  **Enter a Prompt:** Type your query into the input field.
3.  **Get Inference:** Submit the prompt and observe the asynchronous inference process and the generated response.

#### Note on Ollama Models:

Ollama needs to have models downloaded to perform inferences. You can pull models manually using the Ollama CLI. For example, to pull the `qwen:0.6b` model, run:

```bash
docker exec -it deploy-ai-fastapi-ollama-1 ollama pull qwen:0.6b
```

Replace `deploy-ai-fastapi-ollama-1` with the actual name of your Ollama container if it differs.

#### Example API Request (using `curl`):

You can also interact directly with the FastAPI backend:

```bash
curl -X POST http://localhost:8000/generate \
 -H "x-api-key: dev-key-123" \
 -H "Content-Type: application/json" \
 -d '{"model":"qwen:0.6b","prompt":"Write a haiku about the future of AI."}'
```

This will return a `job_id`:

```json
{ "job_id": "some-unique-job-id", "status": "queued" }
```

You can then poll the status endpoint:

```bash
curl http://localhost:8000/status/some-unique-job-id
```

Once completed, the response will include the generated text:

```json
{ "status": "completed", "result": { "text": "Machines learn and grow,
Future minds begin to bloom,
World transformed anew." } }
```

## Monitoring

Access Prometheus metrics at `http://localhost:8000/metrics`. These metrics provide insights into request latency, request counts, and error rates, allowing for effective monitoring and performance analysis.

## Contributing

Contributions are welcome! Please feel free to fork the repository, open issues, or submit pull requests.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
