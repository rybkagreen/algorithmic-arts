from sentence_transformers import SentenceTransformer

MODEL_NAME = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
EMBEDDING_DIM = 768

def load_embedding_model() -> SentenceTransformer:
    """Загружает модель эмбеддингов."""
    return SentenceTransformer(MODEL_NAME)