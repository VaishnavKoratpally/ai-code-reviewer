EVAL_CASES = [
    {
        "query": "load a GitHub repository",
        "expected_keywords": ["load_repo", "clone_repo"]
    },
    {
        "query": "split code into chunks",
        "expected_keywords": ["chunk_file", "AST", "FunctionDef"]
    },
    {
        "query": "build index from chunks",
        "expected_keywords": ["index", "add_chunk", "chunks"]
    }
]

def evaluate_retriever_keywords(retriever, cases, top_k=5):
    total_queries = len(cases)
    hits = 0
    precision_sum = 0
    recall_sum = 0

    for case in cases:
        results = retriever.retrieve(case["query"], top_k=top_k)
        # concatenate all retrieved chunk contents
        retrieved_texts = [r["content"].lower() for r in results]

        expected_keywords = [k.lower() for k in case["expected_keywords"]]
        matched_keywords = sum(
            any(kw in text for text in retrieved_texts) for kw in expected_keywords
        )

        # hit if at least one keyword is matched
        hit = matched_keywords > 0
        hits += int(hit)

        # precision@k = matched / retrieved
        precision = matched_keywords / max(len(retrieved_texts), 1)
        precision_sum += precision

        # recall@k = matched / expected
        recall = matched_keywords / max(len(expected_keywords), 1)
        recall_sum += recall

    hit_rate = hits / total_queries
    avg_precision = precision_sum / total_queries
    avg_recall = recall_sum / total_queries

    return {
        "hit_rate": hit_rate,
        "precision@k": avg_precision,
        "recall@k": avg_recall
    }

