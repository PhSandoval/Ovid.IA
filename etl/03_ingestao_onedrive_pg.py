import os
import sys
import gc
import json
import uuid
import requests
import psycopg2
from PyPDF2 import PdfReader
from psycopg2.extras import Json
from pgvector.psycopg2 import register_vector
from dotenv import load_dotenv

# Garante que o Python enxergue o pacote backend/app
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from backend.app.services.onedrive_service import listar_arquivos_pasta, baixar_arquivo_memoria

load_dotenv()

# Configurações do Banco e Ollama
DB_USER = os.getenv("POSTGRES_USER", "ovidia_user")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "ovidia_password")
DB_DB = os.getenv("POSTGRES_DB", "ovidia_db")
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/embeddings")
EMBEDDING_MODEL = "nomic-embed-text" # ou o modelo que você preferir usar localmente

def obter_conexao():
    """Cria e retorna a conexão com o PostgreSQL via psycopg2."""
    return psycopg2.connect(
        dbname=DB_DB, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT
    )

def gerar_embedding_ollama(texto: str) -> list:
    """Faz a chamada HTTP direta para o Ollama local e extrai o vetor de embeddings."""
    payload = {
        "model": EMBEDDING_MODEL,
        "prompt": texto
    }
    resp = requests.post(OLLAMA_URL, json=payload)
    resp.raise_for_status()
    return resp.json()["embedding"]

def arquivo_ja_processado(conn, onedrive_item_id: str) -> bool:
    """
    Verifica se o onedrive_item_id já existe na coluna JSONB (metadados).
    Útil para evitar retrabalho caso o script seja interrompido.
    """
    cur = conn.cursor()
    cur.execute(
        """
        SELECT 1 FROM jurisprudencia 
        WHERE metadados->>'onedrive_item_id' = %s 
        LIMIT 1;
        """,
        (onedrive_item_id,)
    )
    existe = cur.fetchone() is not None
    cur.close()
    return existe

def fatiar_texto(texto: str, chunk_size: int = 800, overlap: int = 100) -> list[str]:
    """Quebra o texto em partes menores para caber na janela de contexto do LLM."""
    chunks = []
    start = 0
    texto_len = len(texto)
    while start < texto_len:
        end = min(start + chunk_size, texto_len)
        chunks.append(texto[start:end])
        start += (chunk_size - overlap)
    return chunks

def executar_pipeline(folder_id: str = "root"):
    print(f"🚀 Iniciando Pipeline ETL Air-Gap. Lendo pasta: {folder_id}")
    
    conn = obter_conexao()
    register_vector(conn)
    
    # 1. Lista os arquivos do OneDrive via Graph API
    arquivos = listar_arquivos_pasta(folder_id)
    if not arquivos:
        print("Nenhum arquivo encontrado ou falha de conexão com Graph API.")
        return

    print(f"📁 Encontrados {len(arquivos)} arquivos. Iniciando processamento...")

    for arq in arquivos:
        item_id = arq["id"]
        nome = arq["nome"]
        mime = arq.get("mime_type", "")
        
        # Filtra apenas PDFs
        if "pdf" not in mime.lower() and not nome.lower().endswith(".pdf"):
            print(f"⏭️ Ignorando {nome} (Não é PDF)")
            continue
            
        # Controle de Estado (Idempotência)
        if arquivo_ja_processado(conn, item_id):
            print(f"✅ Arquivo já processado anteriormente: {nome}. Pulando...")
            continue
            
        print(f"⬇️ Baixando {nome} para a RAM...")
        
        try:
            # 2. Download diretamente para io.BytesIO (In-Memory)
            buffer_memoria = baixar_arquivo_memoria(item_id)
            
            # 3. Extração de Texto com PyPDF2
            leitor_pdf = PdfReader(buffer_memoria)
            texto_completo = ""
            for pagina in leitor_pdf.pages:
                txt = pagina.extract_text()
                if txt:
                    texto_completo += txt + "\n"
                    
            # Limpeza estrita de memória pós-extração
            buffer_memoria.close()
            del leitor_pdf
            del buffer_memoria
            gc.collect()

            if not texto_completo.strip():
                print(f"⚠️ Aviso: Nenhum texto legível encontrado em {nome}.")
                continue
                
            # 4. Fatiamento (Chunking)
            chunks = fatiar_texto(texto_completo)
            print(f"✂️ Texto fatiado em {len(chunks)} chunks. Gerando embeddings...")
            
            # 5. Geração de Vetores e Ingestão Segura
            cur = conn.cursor()
            for chunk in chunks:
                if not chunk.strip():
                    continue
                    
                vetor = gerar_embedding_ollama(chunk)
                doc_id = str(uuid.uuid4())
                
                # O onedrive_item_id vai pro jsonb para guiar o futuro RAG Small-to-Big
                metadados = {
                    "onedrive_item_id": item_id,
                    "nome_arquivo": nome,
                    "origem": "onedrive"
                }
                
                cur.execute(
                    """
                    INSERT INTO jurisprudencia (id, texto, metadados, vetor)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (doc_id, chunk, Json(metadados), vetor)
                )
                
            conn.commit()
            cur.close()
            print(f"🎉 Sucesso! {nome} ingerido no PostgreSQL.")
            
        except Exception as e:
            conn.rollback()
            print(f"❌ Erro ao processar o arquivo {nome}: {str(e)}")

    conn.close()
    print("🏁 Pipeline ETL finalizado.")

if __name__ == "__main__":
    # Inicia a leitura do drive (folder 'root' ou coloque um folder_id real do OneDrive)
    executar_pipeline(folder_id="root")
