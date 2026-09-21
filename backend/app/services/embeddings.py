from sentence_transformers import SentenceTransformer

# Inicializa o modelo de embeddings (rápido e pequeno para testes locais)
# O modelo será baixado na primeira vez que rodar
try:
    embedder = SentenceTransformer('all-MiniLM-L6-v2')
except Exception as e:
    print(f"Erro ao carregar SentenceTransformer: {e}")
    embedder = None

def gerar_embedding(texto: str) -> list[float]:
    """
    Recebe uma string e retorna um vetor (lista de floats) que a representa matematicamente.
    """
    if not embedder:
        return []
    
    # O método encode retorna um array do numpy, que convertemos para lista nativa do Python
    vetor = embedder.encode(texto).tolist()
    return vetor
