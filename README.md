# 🚀 Prodify AI Inference Gateway

> Scalable async inference system using **FastAPI**, **Celery**, **Redis**, and **Ollama**, with a modern **React (Vite + Shadcn)** frontend.

---

## 🧠 System Overview

```
Frontend (React)
   │  prompts / polls
   ▼
FastAPI Gateway (API + Auth)
   │  queues task
   ▼
Redis (Broker + Backend)
   │  distributes
   ▼
Celery Worker → Ollama (LLM)
   │  results
   ▼
Frontend UI updates
```

---

## ⚙️ Tech Stack

| Layer            | Tech           | Role                         |
| ---------------- | -------------- | ---------------------------- |
| **Frontend**     | React + Shadcn | Async prompt + polling UI    |
| **Gateway**      | FastAPI        | Auth, routing, metrics       |
| **Queue**        | Celery         | Async job management         |
| **Broker/Store** | Redis          | Queue + result storage       |
| **Inference**    | Ollama         | Local models (Qwen, Mistral) |

---

## 📁 Folder Structure

```
app/
 ┣ api/
 ┃ ┣ routes_generate.py   # POST /generate (async job)
 ┃ ┣ routes_status.py     # GET /status/{job_id}
 ┃ ┗ routes_models.py     # GET /models
 ┣ services/
 ┃ ┗ ollama_client.py     # Ollama API wrapper
 ┣ worker.py              # Celery task runner
 ┗ main.py                # FastAPI entrypoint
frontend/
 ┗ src/App.tsx            # Async UI (model + prompt)
```

---

## ⚡ Workflow

1. Frontend calls `/generate` → returns job_id
2. FastAPI enqueues Celery task → Redis
3. Worker pulls task → calls Ollama → stores result
4. Frontend polls `/status/{job_id}` → displays output

---

## 🧩 Example

```bash
curl -X POST http://127.0.0.1:8000/generate \
 -H "x-api-key: dev-key-123" \
 -d '{"model":"qwen3:0.6b","prompt":"Write a haiku about Bangalore."}'
```

```json
{ "job_id": "123abc", "status": "queued" }
```

Later:

```json
{ "status": "completed", "result": { "text": "Bangalore hums bright..." } }
```

---

## 🚀 Highlights

- Async inference via **Celery + Redis**
- Local models served with **Ollama**
- Secure API-key auth
- Modern frontend with **Vite + Shadcn**
- Scalable, fault-tolerant design
