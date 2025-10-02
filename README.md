# LLM Knowledge Extractor

Extract structured knowledge from unstructured text using LLMs.

## Quick Start

### Prerequisites
- Python 3.12+
- [uv](https://github.com/astral-sh/uv) package manager
- OpenAI API key
- Make (optional, for convenience commands)

### Setup (Easy Way - Using Makefile)

```bash
# 1. Clone repository
git clone <your-repo-url>
cd llm-knowledge-extractor

# 2. Setup dependencies (installs everything)
make setup

# 3. Configure environment
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# 4. Run the server
make run

# 5. In another terminal, run tests
make test

# 6. Run LLM quality evaluations
make eval

# See all available commands
make help
```

### Setup (Manual Way)

1. **Clone and install dependencies:**
   ```bash
   git clone <your-repo-url>
   cd llm-knowledge-extractor
   uv sync
   uv pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env and add your OPENAI_API_KEY
   ```

3. **Run the server:**
   ```bash
   uv run uvicorn app.main:app --reload
   ```

4. **Test the API:**
   - API documentation: http://localhost:8000/docs
   - Interactive API: Try the Swagger UI
   - Run tests: `uv run pytest tests/`

## API Endpoints

### `POST /analyze`
Analyze text and extract structured metadata.

**Request:**
```json
{
  "text": "Your text here..."
}
```

**Response:**
```json
{
  "id": 1,
  "summary": "One to two sentence summary",
  "title": "Extracted title or null",
  "topics": ["topic1", "topic2", "topic3"],
  "sentiment": "positive",
  "keywords": ["keyword1", "keyword2", "keyword3"],
  "created_at": "2025-10-01T12:00:00"
}
```

### `GET /search?topic=xyz`
Search analyses by topic or keyword.

**Response:**
```json
{
  "results": [...],
  "count": 5
}
```

## Technology Stack

- **Framework**: FastAPI (async, type-safe, auto-docs)
- **LLM Integration**: DSPy (reliable structured extraction)
- **Database**: SQLite + SQLAlchemy (easy migration path)
- **NLP**: spaCy (manual keyword extraction)
- **Dependencies**: uv + Python 3.12

> For detailed design rationale, assumptions, and improvement roadmap, see [notes.md](notes.md)

## Testing

### Using Makefile (Recommended)

```bash
# Run all tests
make test

# Run only unit tests (fast)
make test-unit

# Run API integration tests (needs server running)
make test-api

# Run LLM quality evaluations (needs server running, costs $$)
make eval
```

### Manual Commands

**Run unit tests (fast, deterministic):**
```bash
uv run pytest tests/ -v
```

**Run integration tests:**
```bash
# Start server first
uv run uvicorn app.main:app --reload

# In another terminal
uv run python tests/test_api.py
```

**Run LLM quality evaluations (slow, costs API credits):**
```bash
# Start server first
uv run uvicorn app.main:app --reload

# In another terminal
uv run python evals/eval_llm_quality.py
```

## Edge Cases Handled

1. **Empty input**: Validated at API layer with Pydantic (returns 422)
2. **LLM API failures**: Gracefully caught and return 503 with clear error message
3. **No nouns in text**: Keyword extraction returns empty list
4. **Invalid JSON from LLM**: Caught and wrapped in appropriate error response
5. **Short text**: Works correctly even with single-sentence inputs

## 🐳 Docker

### Using Makefile

```bash
# Build Docker image
make docker-build

# Run with docker-compose
make docker-run

# View logs
make docker-logs

# Stop containers
make docker-stop

# Open shell in container
make docker-shell
```

### Manual Commands

```bash
docker build -t llm-knowledge-extractor .
docker run -p 8000:8000 --env-file .env llm-knowledge-extractor

# Or with docker-compose
docker-compose up -d
```

## Project Structure

```
llm-knowledge-extractor/
├── app/
│   ├── main.py              # FastAPI application
│   ├── models.py            # Pydantic models
│   ├── database.py          # SQLAlchemy models
│   ├── config.py            # Configuration
│   └── services/
│       ├── llm_service.py   # DSPy LLM integration
│       └── nlp_service.py   # spaCy keyword extraction
├── tests/
│   ├── test_services.py     # Unit tests (fast, deterministic)
│   └── test_api.py          # Integration tests
├── evals/
│   ├── eval_llm_quality.py  # LLM quality evaluations (slow, expensive)
│   └── README.md            # Evals documentation
├── docs/
│   ├── assignment.md        # Original assignment
│   └── plan.md              # Implementation plan
├── Makefile                 # Convenience commands
├── Dockerfile               # Container definition
├── docker-compose.yml       # Container orchestration
├── pyproject.toml           # Project dependencies (uv)
├── README.md                # This file
└── SUBMISSION.md            # Submission summary
```

## Assignment Requirements Checklist

**Core Requirements:**
- [x] Accepts text input via API
- [x] LLM generates 1-2 sentence summary
- [x] Extracts title, topics (3), sentiment
- [x] Keywords extracted manually (spaCy, not LLM)
- [x] Stores analyses in SQLite database
- [x] `POST /analyze` endpoint
- [x] `GET /search?topic=xyz` endpoint
- [x] Handles empty input gracefully
- [x] Handles LLM API failure gracefully
- [x] Basic unit tests for NLP service
- [x] Docker support
- [x] Confidence score (LLM-generated)
- [ ] Batch processing (not implemented)

## Additional Documentation

- **[notes.md](notes.md)** - Design choices, assumptions, limitations, and improvement roadmap
- **[evals/README.md](evals/README.md)** - Why we separate tests from evaluations

---

**Built for Jouster** | October 2025

