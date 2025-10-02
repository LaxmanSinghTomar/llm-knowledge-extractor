# Evaluations (Evals)

## Purpose

This directory contains **quality evaluations** for LLM-powered components, separate from traditional unit/integration tests.

## Why Separate from `tests/`?

### `tests/` (Traditional Testing)
- **Fast**: Runs in seconds
- **Deterministic**: Same input → same output
- **CI/CD**: Run on every commit
- **Cost**: Free (or mocked)
- **Purpose**: Catch regressions, verify logic

### `evals/` (LLM Quality Assessment)
- **Slow**: Takes minutes (multiple API calls)
- **Probabilistic**: May vary slightly across runs
- **Manual**: Run periodically, not in CI
- **Cost**: Real API credits ($$$)
- **Purpose**: Assess output quality, measure accuracy

## Files

- `eval_llm_quality.py` - Comprehensive quality assessment with diverse test cases
  - Tests sentiment accuracy across positive/neutral/negative
  - Evaluates topic extraction relevance
  - Assesses summary quality
  - Validates title extraction logic

## Running Evals

```bash
# Start the server
uv run uvicorn app.main:app --reload

# In another terminal, run evals
uv run python evals/eval_llm_quality.py
```

