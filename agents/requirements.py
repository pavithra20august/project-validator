from __future__ import annotations

from ..models import ProjectSnapshot
from .base import BaseValidationAgent


class RequirementsAgent(BaseValidationAgent):

    @property
    def name(self) -> str:
        return "Requirements Validator"

    @property
    def dimension(self) -> str:
        return "requirements"

    def build_system_prompt(self) -> str:
        return f"""You are a requirements validation agent. Your job is to map each requirement from the requirements document to actual code implementation.

## Evaluation Process

1. **Parse Requirements**: Extract each distinct requirement/feature from the requirements document.
2. **Trace to Code**: For each requirement, find the code files that implement it.
3. **Assess Status**:
   - "implemented": Feature is fully working in the code
   - "partial": Some aspects are implemented but key parts are missing
   - "missing": No code implements this requirement
   - "unclear": Cannot determine from the code alone
4. **Detect Scope Creep**: Identify significant functionality in the code that is NOT mentioned in requirements.

## Scoring
- Score is primarily driven by the percentage of requirements that are "implemented" or "partial".
- Deduct for each "missing" requirement (scaled by total count).
- Scope creep findings are informational — they don't reduce the score but should be flagged.

## requirement_mappings
You MUST populate the `requirement_mappings` array with one entry per requirement found in the document.
Each entry needs: requirement_id (like "REQ-1", "REQ-2"), requirement_text, status, evidence (file paths), and notes.

{self.SCORING_RUBRIC}

Respond with your analysis as structured JSON."""

    def build_user_message(self, snapshot: ProjectSnapshot) -> str:
        if not snapshot.requirements_doc:
            return """No requirements document was found for this project.
Score this as 0.5 with a single finding noting that no requirements document exists.
Set requirement_mappings to an empty array."""

        source_files = self._get_source_files(snapshot)

        return f"""## Requirements Document
{snapshot.requirements_doc}

## Project Structure
{snapshot.directory_structure}

## Source Files
{source_files}

Analyze each requirement against the actual implementation. Populate requirement_mappings for every requirement you find."""
