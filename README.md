# Project Validator

AI-powered codebase review agent that validates any application against requirements and best practices using Claude.

## What It Does

Runs **5 specialized validation agents** against your codebase:

| Agent | What It Checks |
|-------|---------------|
| **Structure** | File organization, essential files (.gitignore, README), dead code |
| **Requirements** | Maps each requirement to code, finds gaps and scope creep |
| **Code Quality** | Patterns, security issues, dependency hygiene, type safety |
| **Architecture** | Separation of concerns, API design, data flow, scalability |
| **Completeness** | Tests, docs, CI/CD, deployment readiness |

Produces a **scored report** (0-100) with:
- Color-coded terminal output
- Styled HTML dashboard with score gauge, findings, and requirements traceability matrix
- JSON export for automation

## Setup

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY="your-key-here"
```

## Usage

```bash
# Validate a project with a requirements doc
PYTHONPATH=. python -m project_validator validate ./my-project --requirements docs/spec.md

# Auto-detect requirements (looks for README.md, requirements.md, etc.)
PYTHONPATH=. python -m project_validator validate ./my-project

# Skip specific dimensions
PYTHONPATH=. python -m project_validator validate ./my-project --skip completeness --skip structure

# Verbose mode (show agent summaries)
PYTHONPATH=. python -m project_validator validate ./my-project -v
```

## Output

Reports are saved to `{project}/.validation-report/`:
- `report.html` — styled dashboard
- `report.json` — machine-readable results

## Architecture

```
project_validator/
├── agents/           # 5 specialized validation agents
│   ├── base.py       # Shared agent framework (Claude API calls)
│   ├── structure.py
│   ├── requirements.py
│   ├── quality.py
│   ├── architecture.py
│   └── completeness.py
├── collectors/       # Codebase file collection & filtering
├── report/           # Terminal (Rich) + HTML report generators
├── orchestrator.py   # Runs agents sequentially, aggregates scores
├── cli.py            # Click-based CLI
└── models.py         # Pydantic data models
```

## Cost

Uses Claude Sonnet 5.5 (`claude-sonnet-5-5`) — approximately **$0.50-0.70 per validation run**.

## License

MIT
