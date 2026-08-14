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
from datetime import datetime
import os
import json

MAX_MODEL_TOKENS = 12000
TOKEN_ESTIMATE_PER_CHAR = 4  
MAX_LINES_PER_CHUNK_FOR_LLM = 50 

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
        selected.append(truncate_chunk(c)) 
        total_chars += estimated_tokens
    return selected

def save_analysis_to_file(analysis, repo_name, metrics, output_dir="output"):
    """Save structured analysis results to a formatted text file."""
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{output_dir}/architecture_analysis_{repo_name}_{timestamp}.txt"
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("ARCHITECTURE ANALYSIS REPORT\n")
        f.write("=" * 80 + "\n\n")
        
        f.write(f"Repository: {repo_name}\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Architecture Summary
        f.write("-" * 80 + "\n")
        f.write("ARCHITECTURE SUMMARY\n")
        f.write("-" * 80 + "\n")
        f.write(analysis.architecture_summary + "\n\n")
        
        # Design Smells
        f.write("-" * 80 + "\n")
        f.write("DESIGN SMELLS\n")
        f.write("-" * 80 + "\n")
        if analysis.design_smells:
            for i, smell in enumerate(analysis.design_smells, 1):
                f.write(f"\n[{i}] {smell.get('name', 'Unknown')}\n")
                f.write(f"    Evidence: {smell.get('evidence', 'N/A')}\n")
                f.write(f"    Why it matters: {smell.get('why_it_matters', 'N/A')}\n")
        else:
            f.write("No design smells detected.\n")
        f.write("\n")
        
        # Scalability Risks
        f.write("-" * 80 + "\n")
        f.write("SCALABILITY RISKS\n")
        f.write("-" * 80 + "\n")
        if analysis.scalability_risks:
            for i, risk in enumerate(analysis.scalability_risks, 1):
                f.write(f"\n[{i}] {risk.get('name', 'Unknown')}\n")
                f.write(f"    Evidence: {risk.get('evidence', 'N/A')}\n")
                f.write(f"    Impact & Mitigation: {risk.get('impact_and_mitigation', 'N/A')}\n")
        else:
            f.write("No scalability risks detected.\n")
        f.write("\n")
        
        # Retriever Metrics
        f.write("-" * 80 + "\n")
        f.write("RETRIEVER PERFORMANCE METRICS\n")
        f.write("-" * 80 + "\n")
        f.write(f"Keyword Retriever:  {json.dumps(metrics['keyword'], indent=2)}\n")
        f.write(f"TF-IDF Retriever:   {json.dumps(metrics['tfidf'], indent=2)}\n")
        f.write(f"Hybrid Retriever:   {json.dumps(metrics['hybrid'], indent=2)}\n\n")
        
        f.write("=" * 80 + "\n")
        f.write("END OF REPORT\n")
        f.write("=" * 80 + "\n")
    
    logger.info(f"Analysis saved to: {filename}")
    print(f"\n✅ Report saved to: {filename}\n")
    return filename


def save_retrieval_details(keyword_results, tfidf_results, hybrid_results, final_results, prompt, repo_name, output_dir="output"):
    """Save detailed retrieval information and prompt for debugging."""
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{output_dir}/retrieval_details_{repo_name}_{timestamp}.txt"
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("RETRIEVAL PIPELINE DETAILS\n")
        f.write("=" * 80 + "\n\n")
        
        f.write(f"Repository: {repo_name}\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Query: 'architecture review design smells scalability risks'\n\n")
        
        # Keyword Retriever Results
        f.write("-" * 80 + "\n")
        f.write("KEYWORD RETRIEVER - TOP RESULTS\n")
        f.write("-" * 80 + "\n")
        for i, chunk in enumerate(keyword_results, 1):
            f.write(f"\n[{i}] FILE: {chunk['file_path']}\n")
            f.write(f"    ID: {chunk['id']}\n")
            f.write(f"    Content Preview (first 300 chars):\n")
            f.write(f"    {chunk['content'][:300]}\n")
            f.write(f"    ...\n")
        
        # TF-IDF Retriever Results
        f.write("\n" + "-" * 80 + "\n")
        f.write("TF-IDF RETRIEVER - TOP RESULTS\n")
        f.write("-" * 80 + "\n")
        for i, chunk in enumerate(tfidf_results, 1):
            f.write(f"\n[{i}] FILE: {chunk['file_path']}\n")
            f.write(f"    ID: {chunk['id']}\n")
            f.write(f"    Content Preview (first 300 chars):\n")
            f.write(f"    {chunk['content'][:300]}\n")
            f.write(f"    ...\n")
        
        # Hybrid Retriever Results
        f.write("\n" + "-" * 80 + "\n")
        f.write("HYBRID RETRIEVER - TOP RESULTS\n")
        f.write("-" * 80 + "\n")
        for i, chunk in enumerate(hybrid_results, 1):
            f.write(f"\n[{i}] FILE: {chunk['file_path']}\n")
            f.write(f"    ID: {chunk['id']}\n")
            f.write(f"    Content Preview (first 300 chars):\n")
            f.write(f"    {chunk['content'][:300]}\n")
            f.write(f"    ...\n")
        
        # Final Selected Chunks (after token budgeting)
        f.write("\n" + "-" * 80 + "\n")
        f.write("FINAL CHUNKS SENT TO LLM (After Token Budgeting)\n")
        f.write(f"Total chunks selected: {len(final_results)}\n")
        f.write("-" * 80 + "\n")
        for i, chunk in enumerate(final_results, 1):
            f.write(f"\n[{i}] FILE: {chunk['file_path']}\n")
            f.write(f"    ID: {chunk['id']}\n")
            f.write(f"    Content:\n")
            f.write(f"    {chunk['content']}\n")
            f.write(f"\n")
        
        # Full Prompt
        f.write("\n" + "=" * 80 + "\n")
        f.write("FULL PROMPT SENT TO LLM\n")
        f.write("=" * 80 + "\n\n")
        f.write(prompt)
        f.write("\n\n" + "=" * 80 + "\n")
        f.write("END OF RETRIEVAL DETAILS\n")
        f.write("=" * 80 + "\n")
    
    logger.info(f"Retrieval details saved to: {filename}")
    print(f"📋 Retrieval details saved to: {filename}")
    return filename


if __name__ == "__main__":
    repo = load_repo(r"C:\Users\61814\source\repos\frigate-dev")
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

    # Retrieve relevant chunks from each retriever
    query = "architecture review design smells scalability risks"
    
    # Get individual retriever results for debugging
    keyword_results = keyword.retrieve(query, top_k=5)
    tfidf_results = tfidf.retrieve(query, top_k=5)
    hybrid_results = retriever.retrieve(query, top_k=5)

    logger.info("\nTop retrieved chunks (pre-truncation):\n")
    # for chunk in hybrid_results:
    #     logger.info(f"FILE: {chunk['file_path']}")
    #     logger.info(chunk["content"][:200])
    #     logger.info("-" * 60)

    # Apply token-budgeting to avoid 413 errors
    safe_results = fit_chunks_to_budget(hybrid_results)
    logger.info(f"Selected {len(safe_results)} chunks under token budget")

    # Build prompt & call LLM
    prompt = build_architecture_prompt(safe_results)
    # logger.info("\n=== PROMPT SENT TO LLM ===\n")
    # logger.info(prompt[:1500])
    
    # Save retrieval details for inspection
    save_retrieval_details(keyword_results, tfidf_results, hybrid_results, safe_results, prompt, repo.repo_name)

    llm_text = run_llm(prompt)
    # logger.info("\n=== RAW LLM OUTPUT ===\n")
    # logger.info(llm_text)

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
    # logger.info(analysis)
    
    # Save analysis to file
    metrics = {
        "keyword": keyword_metrics,
        "tfidf": tfidf_metrics,
        "hybrid": hybrid_metrics
    }
    save_analysis_to_file(analysis, repo.repo_name, metrics)
