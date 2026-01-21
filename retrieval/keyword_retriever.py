class KeywordRetriever:
    ENTRYPOINT_HINTS = {"main", "app", "server", "run", "cli", "__main__"}
    NOISE_PATHS = {"/docs/", "/tests/", "/examples/"}
    LOW_SIGNAL_EXTENSIONS = {".md", ".txt", ".lock", ".json"}

    def __init__(self, index):
        self.index = index

    def _filename_boost(self, path: str) -> float:
        filename = path.lower()
        # Penalize noise folders
        if any(p in filename for p in self.NOISE_PATHS):
            return 0.5
        boost = 1.0
        # Python files 
        if filename.endswith(".py"):
            boost = 1.3
        # Entrypoint heuristics
        if any(name in filename for name in self.ENTRYPOINT_HINTS):
            boost *= 1.2
        return boost

    def _is_low_signal(self, path: str) -> bool:
        p = path.lower()
        if any(p.endswith(ext) for ext in self.LOW_SIGNAL_EXTENSIONS):
            return True
        if any(folder in p for folder in self.NOISE_PATHS):
            return True
        return False
    
    def retrieve(self, query: str, top_k: int = 5):
        keywords = set(query.lower().split()) #Deduplicate keywords to avoid overweighting
        scored = []

        for chunk in self.index.chunks:
            text = chunk["content"].lower()
            path = chunk.get("path", "")
            if self._is_low_signal(path):
                continue
            # Base keyword score
            base_score = sum(text.count(k) for k in keywords)

            if base_score == 0:
                continue

            # Length normalization
            length_penalty = max(len(text), 200)

            # Filename weighting
            boost = self._filename_boost(path)

            final_score = (base_score * boost) / length_penalty

            scored.append((final_score, chunk))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [chunk for _, chunk in scored[:top_k]]
