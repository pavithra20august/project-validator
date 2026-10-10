from __future__ import annotations

import json
from abc import ABC, abstractmethod

import anthropic

from ..models import AgentResult, AgentResultSchema, ProjectSnapshot


class BaseValidationAgent(ABC):

    def __init__(self, client: anthropic.Anthropic, model: str, max_tokens: int):
        self.client = client
        self.model = model
        self.max_tokens = max_tokens

    @property
    @abstractmethod
    def name(self) -> str: ...

    @property
    @abstractmethod
    def dimension(self) -> str: ...

    @abstractmethod
    def build_system_prompt(self) -> str: ...

    @abstractmethod
    def build_user_message(self, snapshot: ProjectSnapshot) -> str: ...

    def analyze(self, snapshot: ProjectSnapshot) -> AgentResult:
        system = self.build_system_prompt()
        user_msg = self.build_user_message(snapshot)

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                thinking={"type": "adaptive"},
                output_config={
                    "effort": "high",
                    "format": {
                        "type": "json_schema",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "score": {
                                    "type": "number",
                                    "minimum": 0.0,
                                    "maximum": 1.0,
                                    "description": "Overall score for this dimension (0.0 to 1.0)"
                                },
                                "findings": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "severity": {
                                                "type": "string",
                                                "enum": ["pass", "info", "warning", "error", "critical"]
                                            },
                                            "category": {"type": "string"},
                                            "title": {"type": "string"},
                                            "description": {"type": "string"},
                                            "file_path": {"type": ["string", "null"]},
                                            "line_number": {"type": ["integer", "null"]},
                                            "recommendation": {"type": "string"}
                                        },
                                        "required": ["severity", "category", "title", "description", "file_path", "line_number", "recommendation"],
                                        "additionalProperties": False
                                    }
                                },
                                "summary": {"type": "string"},
                                "requirement_mappings": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "requirement_id": {"type": "string"},
                                            "requirement_text": {"type": "string"},
                                            "status": {
                                                "type": "string",
                                                "enum": ["implemented", "partial", "missing", "unclear"]
                                            },
                                            "evidence": {
                                                "type": "array",
                                                "items": {"type": "string"}
                                            },
                                            "notes": {"type": "string"}
                                        },
                                        "required": ["requirement_id", "requirement_text", "status", "evidence", "notes"],
                                        "additionalProperties": False
                                    }
                                }
                            },
                            "required": ["score", "findings", "summary", "requirement_mappings"],
                            "additionalProperties": False
                        }
                    }
                },
                system=system,
                messages=[{"role": "user", "content": user_msg}],
            )

            text = next(b.text for b in response.content if b.type == "text")
            parsed = json.loads(text)
            result = AgentResultSchema(**parsed)

            return AgentResult(
                agent_name=self.name,
                dimension=self.dimension,
                score=result.score,
                findings=result.findings,
                summary=result.summary,
                requirement_mappings=result.requirement_mappings,
            )

        except Exception as e:
            return AgentResult(
                agent_name=self.name,
                dimension=self.dimension,
                score=0.0,
                findings=[],
                summary=f"Agent failed: {e}",
                error=str(e),
            )

    def _get_source_files(self, snapshot: ProjectSnapshot) -> str:
        parts = []
        for f in snapshot.file_tree:
            if f.content and f.extension in {".py", ".js", ".ts", ".tsx", ".jsx", ".java", ".go", ".rb", ".rs", ".php", ".html", ".css", ".yaml", ".yml", ".toml", ".json", ".md", ".txt", ".cfg", ".ini", ".sh"}:
                parts.append(f"--- {f.path} ---\n{f.content}\n")
        return "\n".join(parts)

    def _get_config_files(self, snapshot: ProjectSnapshot) -> str:
        config_names = {
            "requirements.txt", "pyproject.toml", "package.json", "setup.py",
            "setup.cfg", "Dockerfile", "docker-compose.yml", "docker-compose.yaml",
            ".gitignore", "Makefile", "tsconfig.json", "webpack.config.js",
            "vite.config.js", "vite.config.ts", ".env", "run.txt",
        }
        parts = []
        for f in snapshot.file_tree:
            name = f.path.split("/")[-1]
            if name in config_names and f.content:
                parts.append(f"--- {f.path} ---\n{f.content}\n")
        return "\n".join(parts)

    SCORING_RUBRIC = """
## Scoring Rubric
- 0.9-1.0: Exemplary. No significant issues. Professional-grade.
- 0.7-0.89: Good. Minor issues only. Ready for production with small fixes.
- 0.5-0.69: Adequate. Several issues that should be addressed. Functional but needs work.
- 0.3-0.49: Below average. Significant gaps or problems.
- 0.0-0.29: Poor. Major structural or quality problems.
"""
