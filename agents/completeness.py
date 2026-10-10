from __future__ import annotations

from ..models import ProjectSnapshot
from .base import BaseValidationAgent


class CompletenessAgent(BaseValidationAgent):

    @property
    def name(self) -> str:
        return "Completeness Validator"

    @property
    def dimension(self) -> str:
        return "completeness"

    def build_system_prompt(self) -> str:
        return f"""You are a project completeness validation agent. Check if the project is production-ready.

## Evaluation Criteria

1. **Test Coverage** (25 points):
   - Test files exist (tests/, __tests__/, *_test.py, *.test.js, etc.)
   - Test framework configured (pytest, jest, mocha, etc.)
   - Tests cover core functionality
   - Both unit and integration tests present

2. **Documentation** (20 points):
   - README with clear setup instructions
   - API documentation (if applicable)
   - Architecture overview
   - Contributing guidelines (for open source)

3. **Environment Setup** (20 points):
   - .env.example with all required variables documented
   - Clear installation steps
   - Dependency installation is automated (pip install -r, npm install)
   - Development vs production configuration

4. **Deployment Readiness** (20 points):
   - Dockerfile or container configuration
   - CI/CD pipeline configuration (.github/workflows/, .gitlab-ci.yml, etc.)
   - Production configuration (CORS, logging, error handling)
   - Health check endpoint (for web services)

5. **Error Monitoring & Logging** (15 points):
   - Logging framework configured
   - Error tracking setup (Sentry, etc.)
   - Request logging for APIs
   - Structured logging format

{self.SCORING_RUBRIC}

Respond with your analysis as structured JSON. Set requirement_mappings to empty array."""

    def build_user_message(self, snapshot: ProjectSnapshot) -> str:
        config_files = self._get_config_files(snapshot)

        readme_content = ""
        for f in snapshot.file_tree:
            name = f.path.split("/")[-1].lower()
            if name in {"readme.md", "readme.txt", "readme"} and f.content:
                readme_content = f"## README Content\n{f.content}\n"
                break

        ci_files = ""
        for f in snapshot.file_tree:
            if any(p in f.path for p in [".github/", ".gitlab-ci", "Jenkinsfile", ".circleci/"]):
                if f.content:
                    ci_files += f"--- {f.path} ---\n{f.content}\n"

        test_files = []
        for f in snapshot.file_tree:
            path_lower = f.path.lower()
            if any(x in path_lower for x in ["test", "spec", "__tests__"]):
                test_files.append(f.path)

        return f"""## Project Structure
{snapshot.directory_structure}

## Total Files: {snapshot.total_files}
## Total Lines: {snapshot.total_lines}

{readme_content}

## Configuration Files
{config_files}

## CI/CD Files
{ci_files if ci_files else "No CI/CD configuration files found."}

## Test Files Found
{chr(10).join(test_files) if test_files else "No test files found."}

Assess the completeness of this project for production readiness."""
