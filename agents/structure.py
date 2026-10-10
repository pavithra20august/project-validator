from __future__ import annotations

from ..models import ProjectSnapshot
from .base import BaseValidationAgent


class StructureAgent(BaseValidationAgent):

    @property
    def name(self) -> str:
        return "Structure Validator"

    @property
    def dimension(self) -> str:
        return "structure"

    def build_system_prompt(self) -> str:
        return f"""You are a project structure validation agent. Analyze the project's file organization and report findings.

## Evaluation Criteria

1. **Essential Files** (25 points):
   - README.md or README exists and has meaningful content
   - Dependency management file exists (requirements.txt, package.json, pyproject.toml, etc.)
   - .gitignore exists and covers common patterns (*.pyc, node_modules, .env, etc.)
   - License file if open source

2. **Directory Organization** (25 points):
   - Logical separation of concerns (backend/frontend, src/tests, etc.)
   - Consistent naming conventions
   - No deeply nested unnecessary directories
   - Source code separated from config/docs

3. **Dead/Orphaned Files** (20 points):
   - No empty files (0 bytes)
   - No obviously abandoned files (backup files, .bak, temp files)
   - No duplicate functionality across files

4. **Documentation** (15 points):
   - Setup/installation instructions exist somewhere
   - Architecture or design documentation
   - API documentation if applicable

5. **Configuration Hygiene** (15 points):
   - .env.example exists if .env is used
   - Build/run scripts or instructions present
   - No secrets committed (check for .env in tracked files)

{self.SCORING_RUBRIC}

Respond with your analysis as structured JSON."""

    def build_user_message(self, snapshot: ProjectSnapshot) -> str:
        file_list = "\n".join(
            f"  {f.path} ({f.size_bytes} bytes)"
            for f in snapshot.file_tree
        )

        config_files = self._get_config_files(snapshot)

        return f"""## Project: {snapshot.root_path}
Total files: {snapshot.total_files}
Total lines: {snapshot.total_lines}
Languages: {snapshot.languages_detected}

## Directory Structure
{snapshot.directory_structure}

## File List with Sizes
{file_list}

## Configuration Files
{config_files}

Analyze this project's structure and provide your findings."""
