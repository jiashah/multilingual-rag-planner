# Multilingual RAG Planner

An AI-powered goal planning app that breaks your goals into actionable daily tasks. It uses RAG over your own documents, supports 11+ languages, and stores your data securely per user.

## Features

- **AI Goal Analysis**: assesses complexity, required skills, and obstacles
- **Smart Task Generation**: creates daily tasks from your goals and uploaded documents (RAG)
- **Multilingual**: English, Spanish, French, German, Italian, Portuguese, Chinese, Japanese, Korean, Hindi, Arabic, with auto-translation and language detection
- **Dashboard**: progress charts, analytics, calendar view, and activity feed
- **Secure Auth**: Supabase Auth with row-level security, so users only see their own data

## Architecture

```
User
 │
 ▼
Streamlit UI
 │
 ├── Authentication ──► Supabase Auth
 │
 ├── Goal Creation ───► Supabase PostgreSQL
 │
 ├── Document Upload
 │        │
 │        ▼
 │    ChromaDB
 │        │
 │        ▼
 │    RAG Retrieval ──► LLM
 │                         │
 │                         ▼
 │                    Task Generation
 │
 └── Progress Tracking ──► Dashboard
```

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit |
| Backend | Python |
| Database & Auth | Supabase (PostgreSQL) |
| AI / ML | OpenAI GPT, LangChain |
| Vector DB | ChromaDB |
| Translation | Google Translate API |

## Quick Start

```bash
git clone https://github.com/yourusername/multilingual-rag-planner.git
cd multilingual-rag-planner
pip install -r requirements.txt
cp .env.example .env   # add your Supabase and OpenAI keys
streamlit run main.py
```

Run `database/schema.sql` in your Supabase SQL editor before the first launch.
