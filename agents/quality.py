from __future__ import annotations

from ..models import ProjectSnapshot
from .base import BaseValidationAgent


class QualityAgent(BaseValidationAgent):

    @property
    def name(self) -> str:
        return "Code Quality Validator"

    @property
    def dimension(self) -> str:
        return "quality"

    def build_system_prompt(self) -> str:
        return f"""You are a code quality validation agent. Review the codebase for quality issues.

## Evaluation Criteria

1. **Coding Patterns & Consistency** (20 points):
   - Consistent naming conventions (snake_case, camelCase, etc.)
   - Consistent code style across files
   - Proper use of language idioms
   - Clean imports (no unused, properly organized)

2. **Error Handling** (20 points):
   - Proper try/except or try/catch coverage
   - Meaningful error messages
   - No bare except clauses catching everything
   - Graceful degradation

3. **Security** (25 points):
   - No hardcoded secrets (API_KEY = "...", password = "...")
   - No SQL injection vulnerabilities (string formatting in queries)
   - No XSS vulnerabilities in template rendering
   - Input validation on user-facing endpoints
   - .env files without .env.example

4. **Dependency Hygiene** (15 points):
   - No unused dependencies in requirements/package files
   - All imported packages listed in dependency files
   - Reasonable version constraints
   - No known vulnerable dependency patterns

5. **Type Safety & Validation** (20 points):
   - Type annotations present (Python type hints, TypeScript types)
   - Data validation at boundaries (Pydantic models, Zod schemas)
   - Consistent use of typed models vs raw dicts

IMPORTANT: The .env file values shown are REDACTED. Do NOT flag redacted values as hardcoded secrets — only flag if you see actual secret patterns in source code files.

{self.SCORING_RUBRIC}

Respond with your analysis as structured JSON. Set requirement_mappings to empty array."""

    def build_user_message(self, snapshot: ProjectSnapshot) -> str:
        source_files = self._get_source_files(snapshot)
        config_files = self._get_config_files(snapshot)

        return f"""## Project Structure
{snapshot.directory_structure}

## Source Files
{source_files}

## Configuration Files
{config_files}

Review this codebase for quality issues. Focus on real, actionable findings."""
