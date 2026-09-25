import uuid
import os
import sys
import csv
import pdfplumber
import docx
from tqdm import tqdm

# Ajuste de Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_DIR = os.path.join(BASE_DIR, "backend")
CSV_PATH = os.path.join(BASE_DIR, "data", "inventario_acervo_interno.csv")
sys.path.insert(0, BACKEND_DIR)

from app.services.vector_db import collection
from app.services.embeddings import gerar_embeddings_em_lote

def extrair_texto_pdf(caminho):
    texto = ""
    try:
        with pdfplumber.open(caminho) as pdf:
            for page in pdf.pages[:10]: # Limita as primeiras 10 pgs para não estourar memória
                page_text = page.extract_text()
                if page_text:
                    texto += page_text + "\n"
    except Exception as e:
        print(f"Erro ao ler PDF {caminho}: {e}")
    return texto

def extrair_texto_docx(caminho):
    texto = ""
    try:
        doc = docx.Document(caminho)
        for para in doc.paragraphs[:50]: # Primeiros 50 parágrafos
            texto += para.text + "\n"
    except Exception as e:
        print(f"Erro ao ler DOCX {caminho}: {e}")
    return texto

def extrair_texto(caminho):
    ext = caminho.lower().split('.')[-1]
    if ext == 'pdf':
        return extrair_texto_pdf(caminho)
    elif ext in ['doc', 'docx']:
        return extrair_texto_docx(caminho)
    return ""

def chunker(seq, size):
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))

def rodar_injecao():
    print("Iniciando Leitura e Injeção dos 1.676 Documentos Reais no ChromaDB...")
    
    with open(CSV_PATH, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        registros = list(reader)
        
    documentos_validos = []
    
    # 1. Extração de Texto dos Arquivos Físicos
    for row in tqdm(registros, desc="Lendo PDFs e DOCXs"):
        caminho = row["Caminho_Absoluto"]
        if not os.path.exists(caminho):
            continue
            
        texto = extrair_texto(caminho).strip()
        if not texto or len(texto) < 100:
            continue
            
        # Pega as primeiras 1000 palavras para vetorizar
        texto_limpo = " ".join(texto.split()[:1000])
        
        documentos_validos.append({
            "id": str(uuid.uuid5(uuid.NAMESPACE_URL, row["Caminho_Absoluto"])),
            "texto": texto_limpo,
            "metadados": {
                "fonte_origem": "Acervo Interno do Escritório",
                "Categoria": row["Categoria"],
                "Tipo_Documento": row["Tipo_Documento"],
                "Ano_Documento": row["Ano_Documento"],
                "Status_Padrao_Ouro": row["Status_Padrao_Ouro"],
                "Partes_Envolvidas": row["Partes_Envolvidas"],
                "Numero_CNJ": row["Numero_CNJ"]
            }
        })
        
    total = len(documentos_validos)
    print(f"Extraídos com sucesso: {total} documentos. Iniciando vetorização GPU (MPS)...")
    
    batch_size = 250
    # 2. Injeção em Massa (Batch)
    for i, lote in enumerate(chunker(documentos_validos, batch_size)):
        print(f"Injetando lote {i+1}/{(total//batch_size)+1}...")
        
        textos = [doc["texto"] for doc in lote]
        ids = [doc["id"] for doc in lote]
        metadados = [doc["metadados"] for doc in lote]
        
        vetores = gerar_embeddings_em_lote(textos, batch_size=64)
        
        collection.add(
            ids=ids,
            embeddings=vetores,
            documents=textos,
            metadatas=metadados
        )
        
    print("✅ ACERVO INJETADO COM SUCESSO! O ChromaDB agora possui o conhecimento interno da firma.")

if __name__ == "__main__":
    rodar_injecao()
