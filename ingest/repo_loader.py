import os
from typing import List
from ingest.types import SourceFile, IngestedRepo


IGNORED_DIRS = {
    ".git",
    "venv",
    "node_modules",
    "__pycache__",
}

MAX_FILE_SIZE = 200_000  # bytes


def infer_language(filename: str) -> str:
    if filename.endswith(".py"):
        return "python"
    return "unknown"


def load_repo(repo_path: str) -> IngestedRepo:
    source_files: List[SourceFile] = []
    repo_name = os.path.basename(os.path.abspath(repo_path))

    for root, dirs, files in os.walk(repo_path):
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]

        for file in files:
            file_path = os.path.join(root, file)

            if os.path.getsize(file_path) > MAX_FILE_SIZE:
                continue

            language = infer_language(file)
            if language == "unknown":
                continue

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
            except Exception:
                continue

            source_files.append(
                SourceFile(
                    path=os.path.relpath(file_path, repo_path),
                    language=language,
                    content=content,
                )
            )

    return IngestedRepo(
        repo_name=repo_name,
        files=source_files,
    )
