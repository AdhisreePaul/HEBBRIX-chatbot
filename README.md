# 🧠 Hebbrix AI Memory System

A memory-augmented conversational AI assistant built for the Hebbrix AI/ML Internship assessment.

This project demonstrates a complete **store → retrieve → use** memory loop with structured fact extraction, semantic retrieval using embeddings, evaluation metrics, and a REST API exposed through a modern React interface.

The focus is not on UI — it is on system reasoning, retrieval quality, and architectural clarity.

---

# 🎯 Problem Statement

Most LLM-based assistants are stateless. They respond based only on the current prompt unless conversation history is manually passed.

This project explores:

> How can an AI assistant remember durable user facts across sessions and use them intelligently in future conversations?

The system implements structured long-term memory storage, semantic similarity retrieval, ranking logic, and personalized response generation.

---

# 🏗️ System Architecture

User (React UI)
↓
Django REST API
↓
Fact Extraction (LLM)
↓
Embedding (Sentence-Transformers)
↓
SQLite Storage (JSON embeddings)
↓
Cosine Similarity Retrieval (Top-K Ranking)
↓
LLM Response Generation (Memory Injected)


The architecture separates concerns into:

- Memory extraction
- Embedding generation
- Retrieval logic
- Chat response generation
- Evaluation pipeline

This modularity improves clarity, extensibility, and testability.

---

# 🧠 Core Design: Store → Retrieve → Use

## 1️⃣ Store — Atomic Memory Extraction

Instead of storing full conversation logs, the system extracts **durable atomic facts**, such as:

- "User is allergic to peanuts."
- "User loves Italian food."
- "User's name is Priya."

Why atomic storage?

- Prevents memory bloat
- Reduces irrelevant context injection
- Improves retrieval precision
- Mimics human abstraction

Each memory stores:

- `content`
- `embedding`
- `importance_score`
- `timestamp`

---

## 2️⃣ Retrieve — Semantic Ranking

When a user asks a question:

1. The query is embedded.
2. All stored memories are compared using cosine similarity.
3. Top-K memories are selected.
4. Final ranking is computed as:
Final Score = 0.8 × similarity + 0.2 × importance_score


This allows:

- Semantic matching
- Adjustable memory prioritization
- Tunable ranking strategy

Top-K retrieval is used instead of Top-1 to improve robustness in downstream generation.

---

## 3️⃣ Use — Memory-Injected Generation

Relevant memories are injected into the system prompt as verified long-term facts.

The LLM is instructed to:

- Treat retrieved memories as authoritative
- Use them naturally in responses
- Maintain short-term conversational continuity

This enables:

> Cross-session personalization without storing entire transcripts.

---

# 🧪 Memory Quality Evaluator

A separate evaluation pipeline tests retrieval performance.

## Dataset

- 10 memory facts
- 10 corresponding queries
- Known ground-truth expected memory

## Metrics

The system computes:

- **Top-1 Accuracy**
- **Top-3 Hit Rate**
- **Mean Reciprocal Rank (MRR)**

### Why these metrics?

- **Top-1** measures strict retrieval correctness.
- **Top-3** reflects practical RAG usage where multiple memories are injected.
- **MRR** captures ranking quality beyond binary correctness.

The goal is not perfect accuracy, but analytical understanding of retrieval behavior.

---

# 📡 REST API Endpoints

| Method | Endpoint | Description |
|--------|----------|------------|
| POST | `/api/memories` | Extract and store new memories |
| GET | `/api/memories/all` | List all stored memories |
| GET | `/api/memories/search?q=` | Semantic search |
| DELETE | `/api/memories/{id}` | Delete memory |
| POST | `/api/chat` | Personalized chat with memory injection |

All endpoints include proper 400 and 404 error handling.

---

# 🎨 Frontend

Built with React.

Features:

- Conversational chatbot UI
- Memory transparency panel
- Typing animation
- Dark mode
- Startup-style polished interface

UI intentionally remains lightweight to emphasize backend reasoning.

---

# ⚙️ Technology Stack

## Backend
- Django
- Django REST Framework
- Sentence-Transformers
- NumPy
- SQLite

## Frontend
- React
- Axios
- Custom CSS (no UI frameworks)

---

# 🧠 Design Tradeoffs

## Why JSON embeddings instead of FAISS / Vector DB?

For this prototype:

- JSONField + cosine similarity is sufficient.
- Simpler to deploy.
- Easier to reason about.

In production:

- FAISS, pgvector, or a vector database would improve scalability and retrieval speed.

---

## Why Top-K instead of Top-1?

LLMs perform better when multiple semantically relevant memories are injected.  
Strict Top-1 retrieval can be brittle under paraphrased queries.

---

## Why store atomic facts instead of full chat logs?

- Reduces token overhead
- Improves retrieval precision
- Prevents noise injection
- Mimics structured long-term memory abstraction

---

# 🚀 Future Improvements

If extended further:

- Memory decay / recency weighting
- Adaptive importance scoring via feedback
- Hybrid search (BM25 + vector similarity)
- Entity-aware filtering
- Deduplication via similarity thresholding
- Vector database integration
- Memory pruning under capacity constraints

---

# 🧩 Human Memory Analogy

Humans:

- Store abstractions, not raw transcripts
- Prioritize important or repeated facts
- Recall via semantic association

This system mimics:

- Durable fact abstraction
- Similarity-based recall
- Importance-weighted ranking

---

# 🏁 How to Run

## Backend

```bash
cd backend
python -m venv venv
# Activate venv (Windows)
venv\Scripts\activate
# Activate venv (Mac/Linux)
source venv/bin/activate

pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

## Frontend

```bash
cd frontend
npm install
npm start


