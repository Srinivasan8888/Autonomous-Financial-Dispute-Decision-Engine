# Autonomous Financial Dispute Decision Engine

An AI-powered decision engine that evaluates financial transaction disputes based on banking regulations (RBI guidelines, NPCI UPI rules, and merchant policies). Built to run on a **strict $0/month budget** utilizing lightning-fast free-tier LLM APIs and local, CPU-friendly vector databases.

Designed to demonstrate production-grade **AI Engineering** concepts such as Agentic Workflows, Advanced RAG, Structured Outputs, and Observability.

## 🧠 Core Architecture

- **Agentic Workflow (LangGraph):** A deterministic state machine that processes dispute metadata, retrieves policies, evaluates the rules against the transaction, and self-reflects if confidence is too low.
- **Advanced Hybrid RAG ($0 Local DB):** Optimizes retrieval using **Dense Vectors (BGE-Small)** combined with **Sparse Vectors (Splade)** for keyword-exact regulation matching. Powered by **FastEmbed** running locally on the CPU.
- **Structured Outputs:** Enforces strict Pydantic JSON schemas via the LLM to ensure the API response is always machine-readable.
- **Audit Logging:** Asynchronously saves every LLM trace and decision into a free-tier **MongoDB Atlas** cluster.
- **Premium Real-Time Dashboard:** A high-end web interface for submitting disputes and visualizing the agent's reasoning chain.
- **Lightning-Fast Inference:** Engineered to use **Groq** APIs (Llama 3 70B) for instant reasoning capabilities, falling back to mock outputs if no keys are provided.

---

## 🎨 Premium Dashboard

We've added a custom-built, modern interface to interact with the engine. It features a "Dark Cocoa & Pearl Cream" aesthetic, glassmorphism UI, and real-time reasoning visualization.

**To access:**

1. Start the server (see below).
2. Open your browser and navigate to `http://localhost:8000/`.

---

## 🧰 Tech Stack

| Component                | Technology            | Cost / Justification          |
| :----------------------- | :-------------------- | :---------------------------- |
| **Backend API**          | FastAPI + Python 3.11 | $0 (Open Source)              |
| **Agent / Orchestrator** | LangGraph & LangChain | $0 (Open Source)              |
| **LLM Inference**        | Groq (Llama 3 8192)   | $0 (Generous Free Tier)       |
| **Vector Embeddings**    | FastEmbed (BGE-Small) | $0 (Runs locally on CPU)      |
| **Vector Database**      | Qdrant (Local)        | $0 (Open Source disk storage) |
| **Audit Database**       | MongoDB Atlas         | $0 (M0 Free Tier forever)     |
| **Observability/LLMOps** | Langfuse              | $0 (Free 50k traces/month)    |

---

## 🚀 Getting Started

### 1. Prerequisites

- Python 3.10 or higher
- Git

### 2. Installation Setup

Clone the repository and set up your virtual isolated environment:

```bash
# Clone the repository
git clone https://github.com/yourusername/autonomous-dispute-engine.git
cd autonomous-dispute-engine

# Create a virtual environment
python -m venv venv

# Activate it
# On Windows:
.\venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install all AI and API dependencies
pip install -r requirements.txt
```

### 3. Environment Variables

Copy the example environment file and fill in your keys:

```bash
cp .env.example .env
```

**Required Keys for full functionality:**

- `GROQ_API_KEY`: Get one for free at [console.groq.com](https://console.groq.com). (If left blank, the system will gracefully mock the LLM output for testing offline).

**Optional Keys (for production tracking):**

- `MONGODB_URI`: Your free-tier MongoDB Atlas connection string.
- `LANGFUSE_PUBLIC_KEY` & `LANGFUSE_SECRET_KEY`: For LLM Token Observability.

### 4. Setup the Vector Database

Before running the API, you must ingest the actual banking regulations (NPCI/RBI rules) into the local Qdrant memory.

```bash
python -m app.data.ingest_docs
```

_This will create a `qdrant_db` folder locally and embed the regulation texts._

---

## 🧪 Testing the Agent Locally (CLI)

You can run the LangGraph reasoning engine directly from the command line without spinning up the backend server:

```bash
python test_graph.py
```

This will inject a dummy "Double Debit" UPI failure dispute into the agent and print the JSON chain-of-thought and final decision to your console.

---

## 🌐 Running the FastAPI Server

To start the production-ready REST API:

```bash
uvicorn app.main:app --reload
```

Navigate your browser to `http://localhost:8000/docs` to see the automated Swagger UI interface.

### Example API Request

**`POST /api/v1/evaluate_dispute`**

```json
{
  "txn_amount": 12500,
  "txn_status": "failed",
  "merchant_type": "ecommerce",
  "dispute_type": "double_debit",
  "txn_time": "22:45",
  "bank": "SBI"
}
```

### Example API Response

```json
{
  "success": true,
  "data": {
    "decision": "Auto Refund Eligible",
    "risk_score": 0.21,
    "confidence": 0.88,
    "policy_clause": "NPCI-ODR-Rule-5.2",
    "reasoning_chain": [
      "Extracted dispute type: 'double_debit' and status: 'failed'.",
      "Retrieved NPCI UPI framework guidelines regarding failed transactions.",
      "Policy states that if a debit occurs on a failed transaction, the issuer must auto-reverse within T+1 days.",
      "Applying rule to SBI transaction of 12500.",
      "Conclusion: User is fully eligible for an automated refund without manual intervention."
    ]
  },
  "error": null
}
```

## 🐳 Docker Deployment (Render / Cloud)

The repository includes a highly-optimized `Dockerfile` configured to pre-cache the HuggingFace models during the build step, ensuring fast startup times on serverless cloud platforms like Render.

```bash
docker build -t dispute-engine .
docker run -p 8000:8000 dispute-engine
```
