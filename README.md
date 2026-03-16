# RoleIQ

RoleIQ is a local-first web app for comparing one resume against one job posting. It parses both inputs into structured data, computes a transparent match score, shows the evidence used for each requirement, and generates grounded resume improvement suggestions without inventing experience.

This repository is organized as:

```text
.
|- apps/
|  |- api/    FastAPI backend, matching engine, scoring, tests, Alembic
|  `- web/    Next.js frontend
|- docker-compose.yml
`- .env.example
```

## Why it exists

Most resume match tools hide the logic behind a single opaque score. This project takes the opposite approach:

- scoring logic lives in application code, not in a single model prompt
- each requirement is matched against explicit resume evidence
- semantic similarity is used as a supporting signal, not the whole decision
- suggestions are constrained to facts already present in the resume

## Core workflow

1. Upload a resume in `PDF`, `DOCX`, or `TXT`
2. Paste a job posting
3. Parse resume text into fragments and structured resume JSON
4. Parse the job posting into requirement items and structured job JSON
5. Match each requirement against resume evidence using:
   - exact normalized term matching
   - lexical overlap
   - PostgreSQL full-text search when Postgres is available
   - embedding similarity when OpenAI embeddings are configured
   - rule-based checks for years, education, and certifications
6. Compute weighted subscores and a transparent overall score
7. Save the analysis so it can be reopened later

## Stack

- Frontend: Next.js App Router, TypeScript, Tailwind CSS
- Backend: FastAPI, SQLAlchemy, Alembic, Pydantic
- Database: PostgreSQL with `pgvector`
- Document parsing: PyMuPDF, python-docx
- Model usage: OpenAI Responses API and embeddings through the official Python SDK

## Running locally

### Prerequisites

- Docker Desktop with Compose

Optional for local non-Docker development:

- Python 3.12+
- Node 20+

### Setup

1. Copy the environment file:

```bash
cp .env.example .env
```

2. Add your `OPENAI_API_KEY` if you want model-backed parsing, semantic embeddings, and grounded rewrite suggestions.

3. Start the stack:

```bash
docker compose up --build
```

4. Open:

- Web UI: [http://localhost:3000](http://localhost:3000)
- API docs: [http://localhost:8000/docs](http://localhost:8000/docs)

### Running migrations manually

```bash
docker compose run --rm api alembic upgrade head
```

## Tests

Backend tests:

```bash
docker compose run --rm api pytest
```

## How scoring works

The score is a weighted fit score, not an ATS simulation.

Default weights:

- Required skills and tools: `30`
- Experience alignment: `25`
- Preferred skills: `15`
- Project and impact relevance: `15`
- Education and certifications: `10`
- Keyword and terminology alignment: `5`

Each job requirement is assigned to one of those buckets. Within a bucket:

- strong matches earn close to full credit
- moderate matches earn partial credit
- weak matches earn limited credit
- missing requirements earn none

The UI exposes:

- bucket-level breakdowns
- requirement-level match strength
- matched and missing terms
- exact resume fragments used as evidence
- caveats when a match is semantic or approximate

If a bucket is not applicable because the posting does not include requirements for it, the overall score is normalized across the remaining active buckets.

## OpenAI usage

The backend uses the OpenAI Python SDK in three places:

- structured resume extraction
- structured job extraction
- embeddings for semantic evidence matching

If `OPENAI_API_KEY` is not set, the app falls back to deterministic extraction and lexical matching so the product still runs locally, but parsed structure and semantic recall are less accurate.

## Limitations

- Resume parsing is intentionally conservative; missing evidence is surfaced instead of guessed.
- PDF text quality depends on the source document.
- Embeddings and structured extraction require an OpenAI API key.
- The MVP stores analyses without authentication because the focus is local evaluation and product clarity.

