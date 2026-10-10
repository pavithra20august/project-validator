import os
from pathlib import Path
from dotenv import load_dotenv


load_dotenv()


ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
MODEL = "claude-sonnet-5-5"
MAX_TOKENS = 16000
MAX_FILE_SIZE_BYTES = 100_000
MAX_TOTAL_CONTEXT_CHARS = 400_000
REPORT_OUTPUT_DIR = ".validation-report"

EXCLUDED_DIRS = {
    ".git", "__pycache__", "node_modules", ".venv", "venv", "env",
    ".mypy_cache", ".pytest_cache", ".tox", "dist", "build",
    ".egg-info", ".eggs", "chroma", "dream_images", ".DS_Store",
    ".validation-report", ".claude",
}

BINARY_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".ico", ".svg", ".webp",
    ".mp3", ".mp4", ".wav", ".avi", ".mov", ".mkv",
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
    ".zip", ".tar", ".gz", ".bz2", ".7z", ".rar",
    ".exe", ".dll", ".so", ".dylib", ".bin",
    ".pyc", ".pyo", ".class", ".o", ".obj",
    ".sqlite", ".sqlite3", ".db",
    ".woff", ".woff2", ".ttf", ".eot", ".otf",
}

DIMENSION_WEIGHTS = {
    "structure": 0.15,
    "requirements": 0.30,
    "quality": 0.25,
    "architecture": 0.15,
    "completeness": 0.15,
}


def get_project_root() -> Path:
    return Path(__file__).parent.parent
