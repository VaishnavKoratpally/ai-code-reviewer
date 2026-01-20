class KeywordRetriever:
    def __init__(self, index):
        self.index = index

    def retrieve(self, query: str, top_k: int = 5):
        keywords = query.lower().split()
        scored = []

        for chunk in self.index.chunks:
            text = chunk["content"].lower()
            score = sum(1 for k in keywords if k in text)

            if score > 0:
                scored.append((score, chunk))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [chunk for _, chunk in scored[:top_k]]
