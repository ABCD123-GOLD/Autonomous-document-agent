# Autonomous Document Agent (RAG Engine)

### Ask Any Document. Get Cited Answers.

---

## 🌟 The Vision: Why This Exists
> *"When the purpose of a thing is not known, abuse is inevitable."*

In the age of AI, many use LLMs as simple toys or search engines. But for businesses, legal teams, and researchers, "guessing" isn't enough. I built this **Autonomous Document Agent** to transform AI from an unpredictable chat-partner into a **dependable knowledge engine**. 

The goal is to provide a system where **truth is verifiable**, **privacy is absolute**, and **scale is unlimited**. This isn't just a chatbot; it's an automated auditor for your private knowledge.

---

## 🚀 Why RAG Over Raw AI?

Using a custom RAG (Retrieval-Augmented Generation) architecture solves the three biggest problems with standard AI:

1.  **Unlimited Knowledge Scale**: You can't paste 1,000 PDFs into ChatGPT. This engine uses **Vector Search** to scan millions of pages and only retrieve the specific context needed for your question.
2.  **Verifiable Truth (Citations)**: Every answer includes **inline citations** (e.g., `[Page 4]`) and a list of **Official Sources**. You never have to "trust" the AI; you can verify it.
3.  **Zero Hallucinations**: By using strict **Grounding Rules**, the AI is forbidden from using its "imagination." If the answer isn't in your documents, it won't make one up.
4.  **Absolute Privacy**: Your documents aren't fed into a public model training set. They stay in your private **Supabase pgvector** database.

---

## 🛠️ Technical Stack (The "Brain")

- **Backend**: FastAPI (Python 3.11) — Production-grade REST API.
- **Reasoning Engine**: OpenAI **GPT-4o** — High-intelligence reasoning and synthesis.
- **Vector Storage**: **Supabase + pgvector** — High-performance semantic retrieval.
- **Interface**: **Telegram Bot** — Drop a PDF and chat instantly from your phone.
- **Architecture**: **RBI Pattern** (Rules, Brain, Implementation) for maximum reliability.

---

## 📦 Getting Started

1.  **Configure Environment**: Copy `.env.example` to `.env` and add your OpenAI, Supabase, and Telegram keys.
2.  **Initialize Database**: Run the provided SQL script in your Supabase SQL Editor to enable `pgvector` and the `match_documents` function.
3.  **Install Dependencies**: `pip install .`
4.  **Launch the Agent**:
    - **API**: `uvicorn app.main:app --reload`
    - **Telegram Bot**: `python -m app.telegram_bot`

---

## 👨‍💻 Built By
**Wuraola Mathew Oladayo**  
*Agentic AI Engineer — Specializing in autonomous, reliable AI systems.*
