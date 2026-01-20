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
if __name__ == "__main__":
    repo = load_repo(".")
    print(f"Loaded {len(repo.files)} source files")
    all_chunks = []
    for file in repo.files:
        chunks = chunk_file(file.path, file.content)
        all_chunks.extend(chunks)
    # print(f"{len(all_chunks)} chunks created")
    index = Indexer()
    for chunk in all_chunks:
        index.add(chunk)
    # print(f"Index size: {index.size()}")
    retriever = KeywordRetriever(index)
    query = "database connection retry timeout scalability"
    results = retriever.retrieve(query, top_k=5)

    # print("\nTop retrieved chunks:\n")

    # for chunk in results:
    #     print(f"FILE: {chunk['file_path']}")
    #     print(chunk["content"][:200])
    #     print("-" * 60)
    prompt = build_architecture_prompt(results)
    # print("\n=== PROMPT SENT TO LLM ===\n")
    # print(prompt[:1500])
    analysis_text = run_llm(prompt)
    print("\n=== RAW LLM OUTPUT ===\n")
    print(analysis_text)
    



