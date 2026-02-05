class HybridRetriever:
    def __init__(self, keyword_retriever, tfidf_retriever, keyword_weight=0.7, tfidf_weight=0.3):
        self.keyword_retriever = keyword_retriever
        self.tfidf_retriever = tfidf_retriever
        self.keyword_weight = keyword_weight
        self.tfidf_weight = tfidf_weight

    def retrieve(self, query: str, top_k: int = 5, expand_top=20):
        """
        Retrieve top_k chunks for a query, combining keyword heuristics + TF-IDF.
        `expand_top` controls how many chunks to retrieve from each before combining.
        """
        # 1️⃣ Get top chunks from each retriever
        kw_results = self.keyword_retriever.retrieve(query, top_k=expand_top)
        tf_results = self.tfidf_retriever.retrieve(query, top_k=expand_top)

        combined_scores = {}
        id_to_chunk = {}

        # 2️⃣ Score keyword chunks with heuristics preserved
        for rank, chunk in enumerate(kw_results):
            cid = chunk["id"]
            # Rank-based score: higher rank → higher score
            score = self.keyword_weight * (1.0 / (rank + 1))
            # Preserve filename boosts if present
            score += chunk.get("file_boost", 0) * 0.1
            combined_scores[cid] = combined_scores.get(cid, 0) + score
            id_to_chunk[cid] = chunk

        # 3️⃣ Score TF-IDF chunks (additive, weaker weight)
        for rank, chunk in enumerate(tf_results):
            cid = chunk["id"]
            score = self.tfidf_weight * (1.0 / (rank + 1))
            combined_scores[cid] = combined_scores.get(cid, 0) + score
            id_to_chunk[cid] = chunk

        # 4️⃣ Sort all chunks by combined score
        final = sorted(
            [(score, id_to_chunk[cid]) for cid, score in combined_scores.items()],
            key=lambda x: x[0],
            reverse=True
        )

        # 5️⃣ Return top_k
        return [chunk for score, chunk in final[:top_k]]
