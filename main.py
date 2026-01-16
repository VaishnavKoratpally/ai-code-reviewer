"""
Pipeline Orchestrator

Responsible for coordinating ingestion, analysis, summarization,
and reasoning stages in sequence.
"""

from ingest.repo_loader import load_repo

if __name__ == "__main__":
    repo = load_repo(".")
    print(f"Loaded {len(repo.files)} source files")
