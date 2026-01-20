class Indexer:
    def __init__(self):
        self.chunks = []

    def add(self, chunk):
        self.chunks.append(chunk)

    def size(self):
        return len(self.chunks)