import torch
from sentence_transformers import SentenceTransformer

# Detectar melhor hardware disponível (MPS para Mac M-Series, CUDA para Nvidia, ou CPU)
device = "cpu"
if torch.backends.mps.is_available():
    device = "mps"
elif torch.cuda.is_available():
    device = "cuda"

try:
    embedder = SentenceTransformer('all-MiniLM-L6-v2', device=device)
    print(f"Modelo de Embeddings carregado no dispositivo: {device.upper()}")
except Exception as e:
    print(f"Erro ao carregar SentenceTransformer: {e}")
    embedder = None

def gerar_embedding(texto: str) -> list[float]:
    """
    Recebe uma string e retorna um vetor (lista de floats) que a representa matematicamente.
    """
    if not embedder:
        return []
    
    vetor = embedder.encode(texto).tolist()
    return vetor

def gerar_embeddings_em_lote(textos: list[str], batch_size=256) -> list[list[float]]:
    """
    Otimização Pesada: Processa uma lista de textos de uma só vez usando batching nativo da placa de vídeo.
    """
    if not embedder:
        return []
    
    # O encode() já é otimizado para lidar com listas e batch sizes
    vetores = embedder.encode(textos, batch_size=batch_size, show_progress_bar=True).tolist()
    return vetores
