from __future__ import annotations

from ..models import ProjectSnapshot
from .base import BaseValidationAgent


class ArchitectureAgent(BaseValidationAgent):

    @property
    def name(self) -> str:
        return "Architecture Validator"

    @property
    def dimension(self) -> str:
        return "architecture"

    def build_system_prompt(self) -> str:
        return f"""You are an architecture validation agent. Evaluate the architectural design of the codebase.

## Evaluation Criteria

1. **Separation of Concerns** (25 points):
   - Clear module boundaries
   - Business logic separated from I/O and presentation
   - Configuration separated from application code
   - Data models in their own module

2. **API Design** (25 points):
   - RESTful or consistent endpoint naming
   - Proper HTTP method usage (GET for reads, POST for writes, etc.)
   - Request/response modeling (typed models, not raw dicts)
   - Consistent error response format
   - Versioning consideration

3. **Data Flow** (20 points):
   - Clear data flow from input to output
   - No circular dependencies between modules
   - Proper use of abstractions (not too many, not too few)
   - State management approach is clear

4. **Frontend/Backend Integration** (15 points):
   - Clean API contract between frontend and backend
   - Proper serialization/deserialization
   - Error handling across the boundary
   - Real-time communication patterns (WebSocket, SSE) if applicable

5. **Scalability Considerations** (15 points):
   - Database/storage abstraction
   - Configuration externalization
   - Stateless design where possible
   - Caching strategy if applicable

{self.SCORING_RUBRIC}

Respond with your analysis as structured JSON. Set requirement_mappings to empty array."""

    def build_user_message(self, snapshot: ProjectSnapshot) -> str:
        source_files = self._get_source_files(snapshot)
        config_files = self._get_config_files(snapshot)

        return f"""## Project Structure
{snapshot.directory_structure}

## Languages Detected
{snapshot.languages_detected}

## Source Files
{source_files}

## Configuration Files
{config_files}

Evaluate the architectural decisions in this codebase."""
