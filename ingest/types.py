from dataclasses import dataclass
from typing import List


@dataclass
class SourceFile:
    path: str
    language: str
    content: str


@dataclass
class IngestedRepo:
    repo_name: str
    files: List[SourceFile]