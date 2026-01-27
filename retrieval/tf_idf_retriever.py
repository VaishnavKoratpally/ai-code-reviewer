from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class TfidfRetriever:
    def __init__(self, chunks):
        self.chunks = chunks
        self.texts = [c["content"] for c in chunks]

        self.vectorizer = TfidfVectorizer(
            stop_words="english",
            max_features=5000,
        )
        self.chunk_matrix = self.vectorizer.fit_transform(self.texts)

    def retrieve(self, query: str, top_k: int = 5):
        query_vec = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vec, self.chunk_matrix)[0]

        scored = list(zip(similarities, self.chunks))
        scored.sort(key=lambda x: x[0], reverse=True)

        return [chunk for score, chunk in scored[:top_k] if score > 0]
