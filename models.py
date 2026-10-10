from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class FileInfo(BaseModel):
    path: str
    size_bytes: int
    extension: str
    content: str | None = None


class ProjectSnapshot(BaseModel):
    root_path: str
    file_tree: list[FileInfo]
    directory_structure: str
    total_files: int
    total_lines: int
    languages_detected: dict[str, int]
    requirements_doc: str | None = None


class Finding(BaseModel):
    severity: Literal["pass", "info", "warning", "error", "critical"]
    category: str
    title: str
    description: str
    file_path: str | None = None
    line_number: int | None = None
    recommendation: str = ""


class RequirementMapping(BaseModel):
    requirement_id: str
    requirement_text: str
    status: Literal["implemented", "partial", "missing", "unclear"]
    evidence: list[str] = Field(default_factory=list)
    notes: str = ""


class AgentResultSchema(BaseModel):
    """Schema for structured output from each validation agent."""
    score: float = Field(ge=0.0, le=1.0)
    findings: list[Finding]
    summary: str
    requirement_mappings: list[RequirementMapping] = Field(default_factory=list)


class AgentResult(BaseModel):
    agent_name: str
    dimension: str
    score: float = Field(ge=0.0, le=1.0)
    findings: list[Finding]
    summary: str
    requirement_mappings: list[RequirementMapping] = Field(default_factory=list)
    error: str | None = None


class ValidationReport(BaseModel):
    project_name: str
    project_path: str
    timestamp: datetime
    overall_score: float
    dimension_scores: dict[str, float]
    agent_results: list[AgentResult]
    requirement_mappings: list[RequirementMapping]
    total_findings: int
    critical_count: int
    error_count: int
    warning_count: int
    pass_count: int
