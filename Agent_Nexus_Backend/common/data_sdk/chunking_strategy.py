from typing import List


class ChunkingStrategy:
    def __init__(self, chunk_size: int = 500, overlap: int = 50):
        if chunk_size <= 0:
            raise ValueError("chunk_size must be positive")
        if overlap < 0:
            raise ValueError("overlap cannot be negative")
        if overlap >= chunk_size:
            raise ValueError("overlap must be smaller than chunk_size")
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, text: str) -> List[str]:
        chunks = []
        start = 0
        length = len(text)
        while start < length:
            end = start + self.chunk_size
            chunks.append(text[start:end])
            start = end - self.overlap
        return chunks
