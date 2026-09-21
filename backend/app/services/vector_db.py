import chromadb
import uuid
import os
from app.services.embeddings import gerar_embedding

# Define o caminho absoluto para a pasta chroma_data na raiz do projeto (Ovid.IA/chroma_data)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
CHROMA_PATH = os.path.join(BASE_DIR, "chroma_data")

# Inicializa o cliente local do ChromaDB salvando os dados na pasta raiz
chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)

# Cria ou obtém a coleção (tabela vetorial) de jurisprudência
collection = chroma_client.get_or_create_collection(name="jurisprudencia")

def adicionar_documento(texto: str, metadados: dict = None) -> str:
    """
    Gera o embedding do texto e salva no banco vetorial.
    """
    vetor = gerar_embedding(texto)
    doc_id = str(uuid.uuid4())
    
    collection.add(
        ids=[doc_id],
        embeddings=[vetor],
        documents=[texto],
        metadatas=[metadados or {}]
    )
    return doc_id

def buscar_similaridade(query: str, limite: int = 3) -> list[dict]:
    """
    Transforma a pergunta num vetor, compara com o banco e retorna os N mais próximos.
    """
    vetor_query = gerar_embedding(query)
    
    # Realiza a busca vetorial (distância cosseno/L2)
    resultados = collection.query(
        query_embeddings=[vetor_query],
        n_results=limite
    )
    
    # Formata a resposta
    documentos_encontrados = []
    
    # O ChromaDB retorna os dados encapsulados em listas para cada query.
    # Como fizemos apenas 1 query, pegamos o índice [0].
    if resultados["documents"] and resultados["documents"][0]:
        for i in range(len(resultados["documents"][0])):
            doc = {
                "texto_recuperado": resultados["documents"][0][i],
                "score": resultados["distances"][0][i], # Menor é mais parecido (L2 distance)
                "metadados": resultados["metadatas"][0][i] if resultados["metadatas"] else {}
            }
            documentos_encontrados.append(doc)
            
    return documentos_encontrados
