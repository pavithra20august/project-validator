from __future__ import annotations

from fnmatch import fnmatch
from pathlib import Path

from ..config import BINARY_EXTENSIONS, EXCLUDED_DIRS, MAX_FILE_SIZE_BYTES
from ..models import FileInfo, ProjectSnapshot


class CodebaseCollector:

    def __init__(self, max_file_size: int = MAX_FILE_SIZE_BYTES):
        self.max_file_size = max_file_size

    def collect(
        self,
        project_path: Path,
        requirements_path: Path | None = None,
    ) -> ProjectSnapshot:
        project_path = project_path.resolve()
        gitignore_patterns = self._load_gitignore(project_path)

        files: list[FileInfo] = []
        total_lines = 0
        languages: dict[str, int] = {}

        for file_path in sorted(project_path.rglob("*")):
            if not file_path.is_file():
                continue

            rel_path = file_path.relative_to(project_path)

            if self._is_excluded(rel_path, gitignore_patterns):
                continue

            ext = file_path.suffix.lower()
            size = file_path.stat().st_size

            content = None
            if ext not in BINARY_EXTENSIONS and size <= self.max_file_size:
                try:
                    raw = file_path.read_text(encoding="utf-8", errors="replace")
                    if file_path.name == ".env":
                        content = self._redact_env(raw)
                    else:
                        content = raw
                    total_lines += content.count("\n") + 1
                except Exception:
                    pass

            lang_key = ext if ext else "(no ext)"
            languages[lang_key] = languages.get(lang_key, 0) + 1

            files.append(FileInfo(
                path=str(rel_path),
                size_bytes=size,
                extension=ext,
                content=content,
            ))

        dir_tree = self._build_tree(project_path, files)

        requirements_doc = None
        if requirements_path and requirements_path.exists():
            requirements_doc = requirements_path.read_text(encoding="utf-8", errors="replace")
        else:
            requirements_doc = self._auto_detect_requirements(project_path)

        return ProjectSnapshot(
            root_path=str(project_path),
            file_tree=files,
            directory_structure=dir_tree,
            total_files=len(files),
            total_lines=total_lines,
            languages_detected=languages,
            requirements_doc=requirements_doc,
        )

    def _load_gitignore(self, project_path: Path) -> list[str]:
        gitignore = project_path / ".gitignore"
        if not gitignore.exists():
            return []
        patterns = []
        for line in gitignore.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                patterns.append(line)
        return patterns

    def _is_excluded(self, rel_path: Path, gitignore_patterns: list[str]) -> bool:
        for part in rel_path.parts:
            if part in EXCLUDED_DIRS:
                return True

        path_str = str(rel_path)
        for pattern in gitignore_patterns:
            if fnmatch(path_str, pattern) or fnmatch(rel_path.name, pattern):
                return True

        return False

    def _redact_env(self, content: str) -> str:
        lines = []
        for line in content.splitlines():
            if "=" in line and not line.strip().startswith("#"):
                key = line.split("=", 1)[0]
                lines.append(f"{key}=<REDACTED>")
            else:
                lines.append(line)
        return "\n".join(lines)

    def _auto_detect_requirements(self, project_path: Path) -> str | None:
        candidates = [
            "requirements.md", "REQUIREMENTS.md", "spec.md", "SPEC.md",
            "docs/requirements.md", "docs/spec.md",
        ]
        for name in candidates:
            path = project_path / name
            if path.exists():
                return path.read_text(encoding="utf-8", errors="replace")

        readme = project_path / "README.md"
        if readme.exists():
            text = readme.read_text(encoding="utf-8", errors="replace")
            if len(text) > 200:
                return text

        for name in ["DreamAI_Documentation.txt", "documentation.txt", "DOCUMENTATION.md"]:
            path = project_path / name
            if path.exists():
                return path.read_text(encoding="utf-8", errors="replace")

        return None

    def _build_tree(self, root: Path, files: list[FileInfo]) -> str:
        dirs: set[str] = set()
        for f in files:
            parts = Path(f.path).parts
            for i in range(1, len(parts)):
                dirs.add("/".join(parts[:i]))

        all_entries = sorted(dirs | {f.path for f in files})

        lines = [root.name + "/"]
        for entry in all_entries:
            depth = entry.count("/")
            name = entry.split("/")[-1]
            prefix = "  " * depth + "├── "
            is_dir = entry in dirs and entry not in {f.path for f in files}
            lines.append(f"{prefix}{name}{'/' if is_dir else ''}")

        return "\n".join(lines)
