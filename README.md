# Production RAG API

### Ask Any Document. Get Cited Answers.

This is a production-grade RAG (Retrieval-Augmented Generation) API built with FastAPI, Supabase, and Gemini Flash. It allows you to upload PDF documents and ask questions via a REST API or a Telegram Bot, receiving answers grounded exclusively in your documents with exact source citations.

---

## 🚀 Why Use This RAG API?

Using a custom RAG architecture is significantly more powerful than simply chatting with a standard AI (like Claude or ChatGPT) for several reasons:

1.  **Unlimited Scale**: Standard AI has a limited "context window." You can't paste 1,000 PDFs into a chat box. This system can handle millions of pages by only retrieving the most relevant snippets for each question.
2.  **Zero Hallucinations**: By using "Grounding," we force the AI to only use the provided document context. If the answer isn't in your files, the AI will say "I don't know" instead of making something up.
3.  **Verifiable Citations**: Every answer comes with exact source citations (e.g., "Document A, Page 5"). This is critical for legal, technical, or business use cases where accuracy is non-negotiable.
4.  **Data Privacy & Ownership**: Your sensitive business data isn't just uploaded to a public chat. It is stored in your private Supabase database, giving you full control over data residency and security.
5.  **Seamless Automation**: Because this is an API, it can be plugged into Telegram, Slack, or your company website to provide 24/7 automated support based on your internal knowledge.

---

## 🛠️ Technical Stack

- **Backend**: FastAPI (Python 3.11)
- **Database**: Supabase + pgvector (Vector Storage)
- **LLM**: Gemini Flash (Reasoning & Generation)
- **Embeddings**: OpenAI `text-embedding-3-small`
- **Interface**: Telegram Bot + REST API (Swagger)
- **Deployment**: Docker + Railway

---

## 📦 Setup & Installation

1.  **Clone the repository**
2.  **Install dependencies**: `pip install .`
3.  **Configure Environment**: Copy `.env.example` to `.env` and fill in your keys.
4.  **Initialize Database**: Run the SQL script provided in the documentation in your Supabase SQL Editor.
5.  **Run the app**: `uvicorn app.main:app --reload`
