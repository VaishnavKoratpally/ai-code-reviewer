"""
Pipeline Orchestrator

Responsible for coordinating ingestion, analysis, summarization,
and reasoning stages in sequence.
"""

from ingest.repo_loader import load_repo
from chunking.chunk_code import chunk_file
from indexing.indexer import Indexer
from retrieval.keyword_retriever import KeywordRetriever
from reasoning.prompts.prompt_builder import build_architecture_prompt
from reasoning.llm_client import run_llm
from reasoning.llm_client import parse_with_retry
from utils.logger import logger

import json
from reasoning.contracts import ArchitectureAnalysis

if __name__ == "__main__":
    repo = load_repo(".")
    logger.info(f"Loaded {len(repo.files)} source files")
    all_chunks = []
    for file in repo.files:
        chunks = chunk_file(file.path, file.content)
        all_chunks.extend(chunks)
    logger.info(f"{len(all_chunks)} chunks created")
    index = Indexer()
    for chunk in all_chunks:
        index.add(chunk)
    retriever = KeywordRetriever(index)
    query = "database connection retry timeout scalability"
    results = retriever.retrieve(query, top_k=5)

    logger.info("\nTop retrieved chunks:\n")

    for chunk in results:
        logger.info(f"FILE: {chunk['file_path']}")
        logger.info(chunk["content"][:200])
        logger.info("-" * 60)
    prompt = build_architecture_prompt(results)
    logger.info("\n=== PROMPT SENT TO LLM ===\n")
    logger.info(prompt[:1500])
    llm_text = run_llm(prompt)
    logger.info("\n=== RAW LLM OUTPUT ===\n")
    logger.info(llm_text)
    parsed_result = parse_with_retry(llm_text)
    analysis = ArchitectureAnalysis(
        architecture_summary=parsed_result["architecture_summary"],
        design_smells=parsed_result["design_smells"],
        scalability_risks=parsed_result["scalability_risks"]
    )
    logger.info(analysis)



