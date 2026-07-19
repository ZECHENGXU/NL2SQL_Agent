from __future__ import annotations

import hashlib
import math
import re


DEFAULT_VECTOR_SIZE = 384


def tokenize_text(text: str) -> list[str]:
    text = text.lower()
    ascii_tokens = re.findall(r"[a-z0-9_]+", text)
    chinese_chars = re.findall(r"[\u4e00-\u9fff]", text)
    chinese_bigrams = [a + b for a, b in zip(chinese_chars, chinese_chars[1:])]
    return ascii_tokens + chinese_chars + chinese_bigrams


class HashingEmbedding:
    """Deterministic local embedding fallback for MVP vector indexing.

    This is not a semantic model. It lets the Qdrant path run without external
    model services, while keeping the embedding interface swappable for bge-m3
    or another local OpenAI-compatible embedding API later.
    """

    def __init__(self, vector_size: int = DEFAULT_VECTOR_SIZE) -> None:
        self.vector_size = vector_size

    def embed(self, text: str) -> list[float]:
        vector = [0.0] * self.vector_size
        for token in tokenize_text(text):
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], "little") % self.vector_size
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            vector[index] += sign

        norm = math.sqrt(sum(value * value for value in vector))
        if norm == 0:
            return vector
        return [value / norm for value in vector]

