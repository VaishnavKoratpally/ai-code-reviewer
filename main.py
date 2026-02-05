from eval_set import EVAL_CASES, evaluate_retriever_keywords
from ingest.repo_loader import load_repo
from indexing.indexer import Indexer
from retrieval.keyword_retriever import KeywordRetriever
from retrieval.tf_idf_retriever import TfidfRetriever
from retrieval.hybrid_retriever import HybridRetriever
from reasoning.prompts.prompt_builder import build_architecture_prompt
from reasoning.llm_client import run_llm, parse_with_retry
from utils.logger import logger
from chunking.ast_chunker import AstChunker
from reasoning.contracts import ArchitectureAnalysis

MAX_MODEL_TOKENS = 12000
TOKEN_ESTIMATE_PER_CHAR = 4  # Rough estimate: 4 chars ≈ 1 token
MAX_LINES_PER_CHUNK_FOR_LLM = 50  # truncate long chunks

def truncate_chunk(chunk, max_lines=MAX_LINES_PER_CHUNK_FOR_LLM):
    lines = chunk["content"].splitlines()
    truncated_lines = lines[:max_lines]
    truncated_chunk = dict(chunk)
    truncated_chunk["content"] = "\n".join(truncated_lines)
    return truncated_chunk

def fit_chunks_to_budget(chunks, max_tokens=MAX_MODEL_TOKENS):
    total_chars = 0
    selected = []
    for c in chunks:
        chunk_chars = len(c["content"])
        estimated_tokens = chunk_chars // TOKEN_ESTIMATE_PER_CHAR
        if total_chars + estimated_tokens > max_tokens:
            break
        selected.append(truncate_chunk(c))  # apply per-chunk truncation
        total_chars += estimated_tokens
    return selected

if __name__ == "__main__":
    repo = load_repo(".")
    logger.info(f"Loaded {len(repo.files)} source files")

    # AST-based chunking
    all_chunks = []
    ast_chunker = AstChunker()
    for file in repo.files:
        chunks = ast_chunker.chunk_file(file.path, file.content)
        all_chunks.extend(chunks)
    logger.info(f"{len(all_chunks)} chunks created")

    # Build index & retrievers
    index = Indexer()
    # Only index relevant project files
    for chunk in all_chunks:
        if ".venv" not in chunk["file_path"]:  # ignore venv, dependencies
            index.add(chunk)


    keyword = KeywordRetriever(index)
    tfidf = TfidfRetriever(index.chunks)
    retriever = HybridRetriever(keyword, tfidf)

    # Retrieve relevant chunks
    query = "architecture review design smells scalability risks"
    results = retriever.retrieve(query, top_k=5)

    logger.info("\nTop retrieved chunks (pre-truncation):\n")
    for chunk in results:
        logger.info(f"FILE: {chunk['file_path']}")
        logger.info(chunk["content"][:200])
        logger.info("-" * 60)

    # Apply token-budgeting to avoid 413 errors
    safe_results = fit_chunks_to_budget(results)
    logger.info(f"Selected {len(safe_results)} chunks under token budget")

    # Build prompt & call LLM
    prompt = build_architecture_prompt(safe_results)
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

    # Evaluate retrievers
    keyword_metrics = evaluate_retriever_keywords(keyword, EVAL_CASES)
    tfidf_metrics = evaluate_retriever_keywords(tfidf, EVAL_CASES)
    hybrid_metrics = evaluate_retriever_keywords(retriever, EVAL_CASES)

    print("Keyword retriever:", keyword_metrics)
    print("TF-IDF retriever:", tfidf_metrics)
    print("Hybrid retriever:", hybrid_metrics)
    logger.info(analysis)
