# Canary

AI-powered sentiment analysis and tracking. Feed it a topic, and it pulls content from across the web, verifies relevance, and scores sentiment using LLMs.

**This project is a work in progress.** It started as an _i-barely-know-what-i'm-doing_ project in 2017 (Twitter streaming + TextBlob) and is being rebuilt from scratch with a modern stack and AI agents. If you want to see the project in its original form (along with some fairly questionable code!), hop over to the `posterity` branch.

## How it works

1. You enter a keyword or topic
2. Source agents fan out to Reddit, NewsAPI, and Bluesky to collect relevant content
3. A verification agent filters out noise, spam, and irrelevant results
4. A sentiment scoring agent analyzes each item and produces structured scores with reasoning
5. Results are persisted and displayed in a dashboard

The agent pipeline is built with [LangGraph](https://github.com/langchain-ai/langgraph) and powered by LLMs via [OpenRouter](https://openrouter.ai).

## Stack

- **Backend:** Python, FastAPI, LangGraph, SQLAlchemy
- **Frontend:** Next.js, TypeScript, Tailwind CSS
- **Database:** PostgreSQL
- **LLM:** OpenRouter (provider-agnostic - GPT-4o-mini by default)

## Local development

You'll need Docker (for Postgres) and API keys for OpenRouter and at least one data source.

```bash
# Start the database
docker compose up db -d

# Backend
cd backend
cp .env.example .env  # then fill in your API keys
uv venv --python 3.12 .venv
source .venv/bin/activate
uv pip install -e ".[dev]"
alembic upgrade head
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Frontend (in a separate terminal)
cd frontend
npm install
npm run dev
```

Open http://localhost:3000 and enter a topic to analyze.
