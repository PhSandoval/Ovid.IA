import os
import json
import uuid
import psycopg2
from psycopg2.extras import Json
from pgvector.psycopg2 import register_vector
from app.services.embeddings import gerar_embedding
from dotenv import load_dotenv

load_dotenv()

# Configurações do PostgreSQL (vem do .env ou usa padrão do docker-compose)
DB_USER = os.getenv("POSTGRES_USER", "ovidia_user")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "ovidia_password")
DB_NAME = os.getenv("POSTGRES_DB", "ovidia_db")
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")

def get_connection():
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        host=DB_HOST,
        port=DB_PORT
    )
    return conn

def inicializar_banco():
    """
    Cria a extensão pgvector e a tabela de jurisprudencia caso não existam.
    """
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        # Habilita a extensão pgvector
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        
        # Cria a tabela principal
        # Note: Usamos 'vector' sem especificar a dimensão para dar flexibilidade (funciona no pgvector >= 0.4.0)
        # O metadado é armazenado como JSONB para permitir buscas relacionais complexas (ex: Categoria = Societário)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS jurisprudencia (
                id UUID PRIMARY KEY,
                texto TEXT NOT NULL,
                metadados JSONB,
                vetor VECTOR
            );
        """)
        
        conn.commit()
        cur.close()
        conn.close()
        print("✅ Banco de Dados (PostgreSQL + pgvector) inicializado com sucesso!")
    except Exception as e:
        print(f"⚠️ Erro ao inicializar o banco de dados: {e}")

# Executa ao importar o módulo
inicializar_banco()


def adicionar_documento(texto: str, metadados: dict = None) -> str:
    """
    Gera o embedding do texto e salva no banco PostgreSQL (pgvector).
    """
    vetor = gerar_embedding(texto)
    doc_id = str(uuid.uuid4())
    
    conn = get_connection()
    register_vector(conn)
    cur = conn.cursor()
    
    try:
        cur.execute(
            """
            INSERT INTO jurisprudencia (id, texto, metadados, vetor)
            VALUES (%s, %s, %s, %s)
            """,
            (doc_id, texto, Json(metadados or {}), vetor)
        )
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()
        
    return doc_id

def buscar_similaridade(query: str, limite: int = 3) -> list[dict]:
    """
    Transforma a pergunta num vetor, compara com o banco usando distância L2
    (operador <->) e retorna os N mais próximos.
    """
    vetor_query = gerar_embedding(query)
    
    conn = get_connection()
    register_vector(conn)
    cur = conn.cursor()
    
    try:
        # O operador <-> calcula a distância Euclidiana (L2) no pgvector.
        # Order by menor distância = maior similaridade.
        cur.execute(
            """
            SELECT texto, metadados, (vetor <-> %s) AS score
            FROM jurisprudencia
            ORDER BY score ASC
            LIMIT %s
            """,
            (vetor_query, limite)
        )
        
        resultados = cur.fetchall()
        
        documentos_encontrados = []
        for row in resultados:
            texto_recuperado, metadados, score = row
            documentos_encontrados.append({
                "texto_recuperado": texto_recuperado,
                "score": float(score),
                "metadados": metadados if metadados else {}
            })
            
        return documentos_encontrados
    
    finally:
        cur.close()
        conn.close()
