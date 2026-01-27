class HybridRetriever:
    def __init__(self, keyword_retriever, tfidf_retriever):
        self.keyword_retriever = keyword_retriever
        self.tfidf_retriever = tfidf_retriever

    def retrieve(self, query: str, top_k: int = 5):
        keyword_results = self.keyword_retriever.retrieve(query, top_k=20)
        tfidf_results = self.tfidf_retriever.retrieve(query, top_k=20)

        combined_scores = {}

        for chunk in keyword_results:
            cid = chunk["id"]
            combined_scores[cid] = combined_scores.get(cid, 0) + 0.3

        for chunk in tfidf_results:
            cid = chunk["id"]
            combined_scores[cid] = combined_scores.get(cid, 0) + 0.6

        final = []
        for chunk in self.tfidf_retriever.chunks:
            cid = chunk["id"]
            if cid in combined_scores:
                score = combined_scores[cid]
                score += chunk.get("file_boost", 0) * 0.1
                final.append((score, chunk))

        final.sort(key=lambda x: x[0], reverse=True)
        return [chunk for score, chunk in final[:top_k]]
