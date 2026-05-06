# PRODUCT REQUIREMENTS DOCUMENT
# Production RAG API
### Ask Any Document. Get Cited Answers.

**Project Metadata**

| Field | Details |
| :--- | :--- |
| **Project** | Production RAG API — Portfolio Project 1 |
| **Version** | 1.0 — Initial Release |
| **Author** | Wuraola M. — AI Automation Engineer |
| **Date** | May 2026 |
| **Status** | **Ready to Build** |
| **Target** | Upwork Portfolio — AI Automation Architect positioning |

---

## 1. Executive Summary

This document defines every requirement needed to build, test, and deploy the **Production RAG API** — a fully deployed FastAPI service that lets any business upload their documents and ask questions, receiving answers grounded exclusively in their own content with exact source citations.

The system is designed as a **portfolio project** that demonstrates production-grade AI engineering skills: FastAPI backend development, vector database integration, Claude API orchestration, API security, observability, and CI/CD deployment. It directly targets the most common and highest-paying Upwork client need in 2026.

| Feature | Details |
| :--- | :--- |
| **Problem it solves** | Businesses cannot query their own documents with AI — they get hallucinated answers or have to paste text manually into ChatGPT |
| **Solution** | Upload any PDF once. Ask questions anytime. Get answers that only use your documents and always cite which chunk they came from. |
| **Who uses it** | SaaS teams, legal firms, ops teams, agencies — anyone with internal knowledge they want to query instantly |
| **Portfolio value** | Demonstrates: FastAPI, pgvector, Claude API, rate limiting, auth, CI/CD, Docker — the full production AI backend stack |

---

## 2. Goals & Non-Goals

### 2.1 Goals — What This Project Must Achieve

| ID | Goal | Why It Matters |
| :--- | :--- | :--- |
| **G-01** | Accept PDF uploads and extract all readable text reliably | Core ingestion capability — no docs in, no answers out |
| **G-02** | Chunk text intelligently and embed using OpenAI text-embedding-3-small | Quality of retrieval directly depends on chunk quality |
| **G-03** | Store and retrieve vectors from Supabase pgvector using cosine similarity | Free, production-grade vector DB — no extra cost for portfolio demo |
| **G-04** | Answer questions using only retrieved context via Claude API — never hallucinate | This is the trust-critical requirement. Clients in legal/ops need cited answers only |
| **G-05** | Return structured JSON with answer + source citations on every response | Downstream systems (n8n, frontends) can parse and route the result |
| **G-06** | Secure every endpoint with API key authentication | Production systems are never open — shows security awareness |
| **G-07** | Rate limit requests to prevent abuse and cost overruns | LLM calls cost money — rate limiting is a production requirement, not optional |
| **G-08** | Log every request with timestamp, endpoint, and response time | Without observability you cannot debug production failures |
| **G-09** | Containerise with Docker and deploy to Railway via GitHub Actions CI/CD | Portfolio must be live and publicly accessible for Upwork clients to test |
| **G-10** | Achieve p95 response time under 8 seconds for the /ask endpoint | Clients will not use a slow AI tool — this is the minimum acceptable UX |

### 2.2 Non-Goals — What This Project Will NOT Build

*   **No frontend UI:** The deliverable is a JSON API exposed via Swagger. A UI can be added later but is not in scope.
*   **No user accounts:** All requests use a single API key. Multi-tenant auth is a future feature.
*   **No real-time streaming:** Claude responses are returned as complete JSON, not streamed tokens. Streaming is a future enhancement.
*   **No file types other than PDF:** Word, Excel, and HTML support are out of scope for v1.
*   **No automatic re-indexing:** When a source document is updated, the user must delete and re-ingest manually.
*   **No fine-tuning:** The system uses Claude off-the-shelf with a system prompt. No model training in scope.

---

## 3. System Architecture

### 3.1 High-Level Architecture

The system has two distinct data flows: Ingestion (documents go in) and Query (questions come out). They share the same vector database but operate independently.

**INGESTION FLOW**
> Client → POST /ingest (PDF file + API Key) → FastAPI validates & extracts text → Chunk into 500-token segments → OpenAI Embeddings API → Supabase pgvector (stored)

**QUERY FLOW**
> Client → POST /ask (question + API Key) → FastAPI validates → OpenAI Embeddings API (embed question) → Supabase cosine similarity search (top 5 chunks) → Claude API (answer from context only) → JSON response with answer + citations

### 3.2 Component Breakdown

| Component | Technology | Responsibility |
| :--- | :--- | :--- |
| API Layer | FastAPI (Python 3.11) | Receive HTTP requests, validate inputs, route to services, return JSON responses |
| PDF Extractor | PyPDF2 | Read PDF bytes, extract text page by page, return as string |
| Text Chunker | Custom Python | Split text into 500-token chunks with 50-token overlap using tiktoken for accurate counting |
| Embedding Service | OpenAI text-embedding-3-small | Convert text chunks and questions into 1536-dimensional float vectors |
| Vector Database | Supabase pgvector | Store chunk embeddings, run cosine similarity search, return top-k matches |
| LLM Service | Anthropic Claude API (claude-sonnet-4-5) | Generate final answer strictly from retrieved context. Return citations. |
| Auth Middleware | FastAPI dependency injection | Validate X-API-Key header on every request. Return 401 if missing or invalid. |
| Rate Limiter | slowapi (Redis or in-memory) | Enforce 20 requests/minute per API key. Return 429 when exceeded. |
| Logger | Python logging (structlog optional) | Emit structured JSON logs: timestamp, endpoint, status_code, response_time_ms, api_key_hash |
| Container | Docker (python:3.11-slim) | Package application with all dependencies for consistent deployment anywhere |
| CI/CD Pipeline | GitHub Actions | On push to main: run pytest, build Docker image, deploy to Railway automatically |
| Hosting | Railway.app (free tier) | Serve live HTTPS endpoint accessible to Upwork clients for portfolio demo |

### 3.3 File Structure
```text
rag-api/
├── app/
│   ├── main.py                     # FastAPI app entry point, middleware setup
│   ├── routes/
│   │   ├── ingest.py               # POST /ingest endpoint
│   │   ├── ask.py                  # POST /ask endpoint
│   │   └── health.py               # GET /health — Railway health check
│   ├── services/
│   │   ├── pdf_extractor.py        # PyPDF2 wrapper
│   │   ├── chunker.py              # Text splitting + tiktoken counting
│   │   ├── embedder.py             # OpenAI embeddings wrapper
│   │   ├── vector_store.py         # Supabase insert + similarity search
│   │   └── llm.py                  # Claude API wrapper + prompt builder
│   ├── middleware/
│   │   ├── auth.py                 # X-API-Key validation dependency
│   │   └── logging.py              # Structured request/response logging
│   ├── models/
│   │   └── schemas.py              # Pydantic request/response models
│   └── config.py                   # Settings from .env via pydantic-settings
├── tests/
│   ├── test_ingest.py
│   ├── test_ask.py
│   └── test_auth.py
├── .github/workflows/deploy.yml    # CI/CD pipeline
├── Dockerfile
├── .env.example
├── pyproject.toml
└── README.md
```

---

## 4. API Endpoints — Full Specification

### 4.1 GET /health
Used by Railway to confirm the service is running. No authentication required.

| Field | Value |
| :--- | :--- |
| Method | GET |
| Auth required | No |
| Rate limited | No |
| 200 response | `{ "status": "healthy", "version": "1.0.0" }` |

### 4.2 POST /ingest
Accepts a PDF file, extracts text, chunks it, embeds each chunk, and stores vectors in Supabase. This is the document loading step.

**Request**

| Field | Details |
| :--- | :--- |
| Content-Type | multipart/form-data |
| Header: X-API-Key | Required. String. The secret API key set in environment variables. |
| Body: file | Required. PDF file. Max size: 10MB. MIME type must be application/pdf. |
| Body: source_name | Optional. String. Human-readable label for this document. Defaults to filename. |

**Response — 200 Success**
```json
{ "status": "success", "source": "company_faq.pdf", "chunks_ingested": 47, "processing_time_ms": 3241 }
```

**Response — Error Codes**

| Code | Condition | Response body |
| :--- | :--- | :--- |
| 400 | File is not a PDF or is corrupted | `{ "detail": "Invalid file type. Only PDF accepted." }` |
| 400 | File exceeds 10MB | `{ "detail": "File too large. Maximum 10MB." }` |
| 401 | Missing or wrong X-API-Key | `{ "detail": "Invalid or missing API key." }` |
| 422 | PDF has no extractable text (scanned image PDF) | `{ "detail": "No text extracted. PDF may be image-only." }` |
| 429 | Rate limit exceeded (20 req/min) | `{ "detail": "Rate limit exceeded. Retry after 60 seconds." }` |
| 500 | Supabase insert failed or OpenAI API error | `{ "detail": "Internal error. See logs." }` |

**Internal Processing Steps**
1. **Validate:** Check file MIME type is application/pdf and size is under 10MB
2. **Extract:** Pass PDF bytes to PyPDF2, iterate pages, concatenate text. Raise 422 if empty.
3. **Chunk:** Use tiktoken cl100k_base tokenizer. Split at 500 tokens with 50-token overlap. Minimum chunk size: 50 tokens (discard smaller).
4. **Embed:** Call OpenAI text-embedding-3-small on each chunk. Batch up to 100 at a time to minimise API calls.
5. **Store:** Insert each row to Supabase: {id: uuid4, content: chunk_text, embedding: vector, source: source_name, chunk_index: int, ingested_at: UTC timestamp}.
6. **Return:** Return 200 with summary JSON including chunk count and processing time.

### 4.3 POST /ask
The core query endpoint. Accepts a natural language question, retrieves the most relevant document chunks, and asks Claude to answer strictly from that context. Returns a structured answer with source citations.

**Request**

| Field | Details |
| :--- | :--- |
| Content-Type | application/json |
| Header: X-API-Key | Required. String. |
| Body: question | Required. String. The natural language question to answer. Max 1000 characters. |
| Body: top_k | Optional. Integer. Number of chunks to retrieve. Default: 5. Min: 1. Max: 10. |
| Body: source_filter | Optional. String. If provided, only search chunks from this source document. |

**Response — 200 Success**
```json
{
  "answer": "The refund policy allows returns within 30 days of purchase...",
  "sources": [
    { "source": "returns_policy.pdf", "chunk_index": 3, "excerpt": "Customers may return..." },
    { "source": "returns_policy.pdf", "chunk_index": 4, "excerpt": "Returns initiated after..." }
  ],
  "confidence": "high",
  "processing_time_ms": 2187
}
```

**Claude Prompt Template — CRITICAL**
This prompt controls the entire quality of the system. Every word matters:

```text
SYSTEM: You are a precise document assistant. Answer questions using ONLY the context
provided below. Do not use any external knowledge. If the answer is not in the context,
respond exactly: 'I could not find this information in the provided documents.'
Never make up information. Never guess. Cite your sources.

CONTEXT:
[retrieved chunks inserted here with chunk index and source label]

USER: [question from API request]
```

**Response — Error Codes**

| Code | Condition | Response body |
| :--- | :--- | :--- |
| 400 | Question is empty or over 1000 characters | `{ "detail": "Question must be 1–1000 characters." }` |
| 401 | Missing or wrong API key | `{ "detail": "Invalid or missing API key." }` |
| 404 | source_filter provided but no matching documents found | `{ "detail": "No documents found for source_filter value." }` |
| 429 | Rate limit exceeded | `{ "detail": "Rate limit exceeded. Retry after 60 seconds." }` |
| 503 | Claude API or Supabase unavailable | `{ "detail": "Upstream service unavailable. Retry shortly." }` |

**Internal Processing Steps**
1. **Validate:** Check question length. Validate top_k range.
2. **Embed question:** Call OpenAI text-embedding-3-small on the question string.
3. **Retrieve:** Run Supabase cosine similarity query. Apply source_filter if provided. Return top_k chunks ordered by similarity score.
4. **Check threshold:** If highest similarity score < 0.70, return low-confidence answer with caveat in response.
5. **Build prompt:** Insert retrieved chunks into the system prompt template. Include source labels and chunk indexes.
6. **Call Claude:** Send to claude-sonnet-4-5 with max_tokens=1024. Temperature=0 for deterministic answers.
7. **Parse + return:** Construct response JSON with answer, source citations, and processing time.

---

## 5. Data Models

### 5.1 Supabase Table: documents

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| id | uuid | PRIMARY KEY, DEFAULT gen_random_uuid() | Unique identifier for each chunk |
| content | text | NOT NULL | Raw text of the chunk |
| embedding | vector(1536) | NOT NULL | 1536-dim float array from OpenAI |
| source | text | NOT NULL | Filename or source_name label |
| chunk_index | integer | NOT NULL | Position of chunk in source document |
| ingested_at | timestamptz | DEFAULT now() | UTC timestamp when row was inserted |
| token_count | integer | | Number of tokens in this chunk (for debugging) |

### 5.2 Pydantic Request/Response Schemas

**IngestResponse**
| Field | Type | Description |
| :--- | :--- | :--- |
| status | str | "success" or "error" |
| source | str | Source name used for storage |
| chunks_ingested | int | Number of chunks stored in Supabase |
| processing_time_ms | int | Total time from request received to response sent |

**AskRequest**
| Field | Type | Validation |
| :--- | :--- | :--- |
| question | str | Required. min_length=1, max_length=1000 |
| top_k | int | Optional. ge=1, le=10, default=5 |
| source_filter | str \| None | Optional. If provided, restricts search to this source |

**SourceCitation**
| Field | Type | Description |
| :--- | :--- | :--- |
| source | str | Source document name |
| chunk_index | int | Position in document for traceability |
| excerpt | str | First 200 characters of the retrieved chunk |
| similarity_score | float | Cosine similarity score (0.0 to 1.0) — for debugging |

**AskResponse**
| Field | Type | Description |
| :--- | :--- | :--- |
| answer | str | Claude's answer using only the retrieved context |
| sources | list[SourceCitation] | List of chunks Claude used to form the answer |
| confidence | str | "high" (score > 0.85), "medium" (0.70-0.85), "low" (< 0.70) |
| processing_time_ms | int | Total server-side processing time |

---

## 6. Environment Variables

All secrets are loaded from environment variables via pydantic-settings. Never hardcode values. The .env file is git-ignored.

| Variable | Required | Description |
| :--- | :--- | :--- |
| API_KEY | **Yes** | Secret key for X-API-Key header auth. |
| ANTHROPIC_API_KEY | **Yes** | Your Anthropic API key from console.anthropic.com |
| OPENAI_API_KEY | **Yes** | Your OpenAI key — used only for text-embedding-3-small |
| SUPABASE_URL | **Yes** | Your Supabase project URL, e.g. https://xyz.supabase.co |
| SUPABASE_SERVICE_KEY | **Yes** | Supabase service_role key (not anon key) — needed for direct DB writes |
| CLAUDE_MODEL | No | Defaults to claude-sonnet-4-5. Override to test other models. |
| MAX_FILE_SIZE_MB | No | Defaults to 10. Max PDF upload size in megabytes. |
| RATE_LIMIT_PER_MINUTE | No | Defaults to 20. Requests per minute per API key. |
| LOG_LEVEL | No | Defaults to INFO. Set to DEBUG during development. |
| ENVIRONMENT | No | development or production. Controls log verbosity and error detail. |

---

## 7. Testing Requirements

### 7.1 Required Test Cases

| Test ID | Test name | What it proves |
| :--- | :--- | :--- |
| T-01 | test_ingest_valid_pdf_returns_200 | Happy path ingestion works end to end |
| T-02 | test_ingest_non_pdf_returns_400 | File type validation rejects non-PDFs |
| T-03 | test_ingest_no_api_key_returns_401 | Auth middleware blocks unauthenticated requests |
| T-04 | test_ingest_wrong_api_key_returns_401 | Auth middleware rejects wrong keys |
| T-05 | test_ask_valid_question_returns_answer | Happy path query returns answer with sources |
| T-06 | test_ask_response_has_citations | Sources field is non-empty on successful answers |
| T-07 | test_ask_empty_question_returns_400 | Input validation rejects empty questions |
| T-08 | test_ask_question_over_1000_chars_returns_400 | Input validation enforces length limit |
| T-09 | test_health_returns_200_no_auth | Health check works without API key |
| T-10 | test_chunk_count_matches_ingested_count | Chunking logic produces expected number of chunks |
| T-11 | test_rate_limit_returns_429_after_threshold | Rate limiter correctly blocks excess requests |
| T-12 | test_source_filter_restricts_search | source_filter param limits retrieval to correct document |

### 7.2 How to Run Tests
```bash
pip install pytest pytest-asyncio httpx
pytest tests/ -v --asyncio-mode=auto
```
Tests use a `TestClient` with a mock Supabase and mock OpenAI/Claude to avoid real API calls during CI. Integration tests against the live stack are run manually before release.

---

## 8. Deployment — Step by Step

### 8.1 Docker Configuration
The Dockerfile must produce a minimal image:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml .
RUN pip install --no-cache-dir .
COPY app/ ./app/
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 8.2 GitHub Actions CI/CD Pipeline
File location: `.github/workflows/deploy.yml`

| Step | Action | Condition |
| :--- | :--- | :--- |
| 1 | Checkout code | On every push to main branch |
| 2 | Set up Python 3.11 | Always |
| 3 | Install dependencies | Always |
| 4 | Run pytest | Always — deploy is BLOCKED if any test fails |
| 5 | Deploy to Railway via Railway CLI | Only if all tests pass on push to main |
| 6 | Notify deployment status | Send success/failure to Slack (optional) |

### 8.3 Railway Setup

1. Create account at railway.app and install Railway CLI: `npm install -g @railway/cli`
2. Login: `railway login`
3. In your project folder: `railway init` then `railway link`
4. Set all environment variables in Railway dashboard under Settings > Variables
5. Push to main — GitHub Actions triggers and deploys automatically
6. Your live URL is available in Railway dashboard. Format: `https://your-app.up.railway.app`
7. Test the live endpoint: `curl https://your-app.up.railway.app/health`

---

## 9. Performance & Security Requirements

### 9.1 Performance Targets

| Metric | Target | Why This Number |
| :--- | :--- | :--- |
| POST /ask p50 response time | < 4 seconds | Acceptable UX for AI-powered search |
| POST /ask p95 response time | < 8 seconds | Hard ceiling — above this users think it is broken |
| POST /ingest (10 page PDF) | < 15 seconds | Ingestion is async-friendly but must complete reliably |
| GET /health | < 200ms | Railway uses this for uptime checks |
| Railway free tier uptime | > 95% | Portfolio must be live when clients visit |

### 9.2 Security Requirements

*   **API Key rotation:** The API_KEY env var can be changed without redeployment (Railway redeploys on env var change).
*   **No key logging:** Never log the raw API key value. Log only a hash or the first 8 characters for debugging.
*   **HTTPS only:** Railway provides HTTPS automatically. Never expose HTTP in production.
*   **Input sanitisation:** Validate all user inputs with Pydantic before passing to any external API or database.
*   **Dependency pinning:** Pin all library versions in pyproject.toml to prevent supply chain issues.
*   **No secrets in code:** All secrets via environment variables. .env is in .gitignore. Verify this before first commit.
*   **Supabase row-level security:** Enable RLS on the documents table in production even if all rows use the same key.

---

## 10. Portfolio Presentation Guide

How to present this project on your Upwork portfolio to maximise conversion.

### 10.1 Portfolio Title
**Production RAG API — Document Q&A with Source Citations | FastAPI · Supabase · Claude · CI/CD**

### 10.2 Portfolio Description (copy this)
Built a production FastAPI service that ingests PDF documents, embeds them into Supabase pgvector, and answers natural language questions using Claude API with exact source citations. Every answer only uses the uploaded documents — no hallucinations, no external knowledge.

Technical highlights: API key authentication, 20 req/min rate limiting, structured JSON logging, 12 pytest tests, Dockerfile, and GitHub Actions CI/CD pipeline to Railway. Live endpoint available for testing via Swagger UI.

### 10.3 Loom Demo Script (3 minutes)
1. **0:00–0:30** — Show the Swagger UI at your live Railway URL. Point out the two endpoints. Briefly explain what RAG means in plain English.
2. **0:30–1:15** — Upload a PDF (use a 2-page company FAQ). Show the 200 response with chunks_ingested count. Show the Railway logs tailing in the background.
3. **1:15–2:15** — Ask a specific question that is answered in the PDF. Show the JSON response with the answer and sources array. Then ask a question NOT in the PDF — show it returns the 'not found' message instead of making something up.
4. **2:15–2:45** — Show the GitHub Actions tab — green checkmark on the last deploy. Show the Dockerfile and the workflow YAML briefly.
5. **2:45–3:00** — Summarise: 'This is what I build for clients — production systems that are deployed, secured, and documented on day one.'

### 10.4 What Screenshots to Include

| # | Screenshot | What it proves |
| :--- | :--- | :--- |
| 1 | FastAPI Swagger UI at live HTTPS Railway URL | It is deployed — not running locally |
| 2 | POST /ask response JSON showing answer + sources array | The core output is structured and citable |
| 3 | GitHub Actions — green deploy workflow on main branch | CI/CD is real and working |
| 4 | Supabase Table Editor showing documents rows with embeddings | Vector storage is real, not mocked |
| 5 | pytest output showing 12 passing tests | Production instinct — code has test coverage |

---

## 11. Recommended Build Timeline

| Day | Task | Deliverable |
| :--- | :--- | :--- |
| Day 1 | Set up project structure, pyproject.toml, .env, Supabase table creation, pgvector extension | Project scaffold + DB ready |
| Day 2 | Build PDF extractor service, chunker with tiktoken, unit test both services | T-01, T-02, T-10 passing |
| Day 3 | Build embedder service (OpenAI), vector_store service (Supabase insert + search), unit test both | Embedding + storage working |
| Day 4 | Build POST /ingest endpoint, auth middleware, file validation, integration test | T-01 to T-04 passing |
| Day 5 | Build LLM service (Claude prompt template), POST /ask endpoint, end-to-end test | T-05, T-06, T-07 passing |
| Day 6 | Add rate limiter (slowapi), structured logging middleware, remaining tests | T-08 to T-12 passing |
| Day 7 | Write Dockerfile, test Docker build locally, write GitHub Actions workflow | Container builds cleanly |
| Day 8 | Deploy to Railway, verify live endpoint, set all env vars in Railway dashboard | Live HTTPS URL active |
| Day 9 | Write README with architecture diagram, setup instructions, curl examples | GitHub repo presentation-ready |
| Day 10 | Record Loom demo, take screenshots, write portfolio description, upload to Upwork | Portfolio entry live |

---

## 12. Dependency Reference

| Library | Version (pin) | Purpose |
| :--- | :--- | :--- |
| fastapi | >=0.111 | Web framework — routes, validation, dependency injection |
| uvicorn[standard] | >=0.29 | ASGI server to run FastAPI |
| anthropic | >=0.28 | Official Anthropic Python SDK for Claude API calls |
| openai | >=1.30 | OpenAI SDK — used only for text-embedding-3-small |
| supabase | >=2.4 | Supabase Python client for pgvector queries and inserts |
| pypdf2 | >=3.0 | PDF text extraction |
| tiktoken | >=0.7 | OpenAI tokenizer — accurate token counting for chunking |
| pydantic-settings | >=2.2 | Load and validate env vars into settings object |
| slowapi | >=0.1.9 | Rate limiting middleware for FastAPI |
| python-multipart | >=0.0.9 | Required by FastAPI for file upload handling |
| pytest | >=8.0 | Test runner |
| pytest-asyncio | >=0.23 | Async test support for FastAPI endpoints |
| httpx | >=0.27 | HTTP client used by FastAPI TestClient |