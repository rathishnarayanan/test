"""Mock embedding adapter — returns deterministic pseudo-random vectors."""
import hashlib
import math
from app.adapters.base import EmbeddingAdapter, EmbeddingResult

VECTOR_DIM = 768


def _text_to_vector(text: str) -> list[float]:
    """Deterministic pseudo-random unit vector from text hash."""
    seed = int(hashlib.sha256(text.encode()).hexdigest(), 16)
    vec = []
    for i in range(VECTOR_DIM):
        # LCG-style deterministic values
        seed = (seed * 6364136223846793005 + 1442695040888963407) & 0xFFFFFFFFFFFFFFFF
        vec.append((seed / 0xFFFFFFFFFFFFFFFF) * 2 - 1)
    magnitude = math.sqrt(sum(v * v for v in vec))
    return [v / magnitude for v in vec]


class MockEmbeddingAdapter(EmbeddingAdapter):
    async def embed(self, text: str) -> EmbeddingResult:
        return EmbeddingResult(vector=_text_to_vector(text), mock=True)
