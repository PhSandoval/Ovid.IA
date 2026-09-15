from sentence_transformers import SentenceTransformer
from typing import List

# Inicializa o modelo de embeddings leve.
# Instanciado globalmente para ser carregado na memória apenas uma vez na inicialização da API.
modelo_embedding = SentenceTransformer('all-MiniLM-L6-v2')

def gerar_embedding(texto: str) -> List[float]:
    """
    Gera um embedding (vetor denso) para o texto fornecido.
    Retorna uma lista de floats representando o texto no espaço vetorial.
    """
    # O método encode retorna um numpy array, que convertemos para uma lista nativa do Python
    vetor = modelo_embedding.encode(texto)
    return vetor.tolist()
