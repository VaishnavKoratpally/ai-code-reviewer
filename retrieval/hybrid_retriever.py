class HybridRetriever:
    def __init__(self, keyword_retriever, tfidf_retriever, keyword_weight=0.1, tfidf_weight=0.9, use_consensus=True):
        """
        Improved hybrid retriever with better weighting.
        
        Args:
            keyword_retriever: Keyword-based retriever
            tfidf_retriever: TF-IDF based retriever
            keyword_weight: Weight for keyword results (default 0.1 = 10%)
            tfidf_weight: Weight for TF-IDF results (default 0.9 = 90%)
            use_consensus: If True, boost chunks appearing in both results
        """
        self.keyword_retriever = keyword_retriever
        self.tfidf_retriever = tfidf_retriever
        self.keyword_weight = keyword_weight
        self.tfidf_weight = tfidf_weight
        self.use_consensus = use_consensus

    def retrieve(self, query: str, top_k: int = 5, expand_top=20):
        """
        Retrieve top_k chunks using improved hybrid scoring.
        
        Strategy:
        1. TF-IDF is the primary signal (90% weight) - more reliable
        2. Keyword is secondary (10% weight) - catches obvious patterns
        3. Consensus boost: chunks appearing in BOTH results get extra credit
        
        Args:
            query: Search query
            top_k: Number of results to return
            expand_top: How many to retrieve from each retriever before combining
        """
        # 1️⃣ Get top chunks from each retriever
        kw_results = self.keyword_retriever.retrieve(query, top_k=expand_top)
        tf_results = self.tfidf_retriever.retrieve(query, top_k=expand_top)

        # 2️⃣ Track which chunks appear in both results (consensus)
        kw_ids = {chunk["id"] for chunk in kw_results}
        tf_ids = {chunk["id"] for chunk in tf_results}
        consensus_ids = kw_ids & tf_ids  # intersection = chunks in both

        combined_scores = {}
        id_to_chunk = {}

        # 3️⃣ Score TF-IDF chunks (PRIMARY SIGNAL)
        for rank, chunk in enumerate(tf_results):
            cid = chunk["id"]
            # Rank-based score: higher rank → higher score
            score = self.tfidf_weight * (1.0 / (rank + 1))
            
            # 🎯 Consensus boost: if chunk appears in keyword results too, it's more reliable
            if self.use_consensus and cid in consensus_ids:
                score *= 1.5  # 50% confidence boost
            
            combined_scores[cid] = combined_scores.get(cid, 0) + score
            id_to_chunk[cid] = chunk

        # 4️⃣ Score keyword chunks (SECONDARY SIGNAL)
        for rank, chunk in enumerate(kw_results):
            cid = chunk["id"]
            # Lighter scoring since keyword retriever is noisy
            score = self.keyword_weight * (1.0 / (rank + 1))
            
            # Only add if not already scored by TF-IDF
            # (prevents noisy keyword results from boosting weak TF-IDF matches)
            if cid not in combined_scores:
                combined_scores[cid] = score
            # If already in TF-IDF results, the TF-IDF score is primary
            
            id_to_chunk[cid] = chunk

        # 5️⃣ Sort all chunks by combined score
        final = sorted(
            [(score, id_to_chunk[cid]) for cid, score in combined_scores.items()],
            key=lambda x: x[0],
            reverse=True
        )

        # 6️⃣ Return top_k
        return [chunk for score, chunk in final[:top_k]]
