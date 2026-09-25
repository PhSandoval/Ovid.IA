import pandas as pd
import json
import uuid
import os
import sys
import math

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_DIR = os.path.join(BASE_DIR, "backend")
DATA_DIR = os.path.join(BASE_DIR, "data")

sys.path.insert(0, BACKEND_DIR)

try:
    from datasets import load_dataset
except ImportError:
    load_dataset = None

from app.services.vector_db import collection
from app.services.embeddings import gerar_embeddings_em_lote

def padronizar_dados(fonte_nome, df, map_processo, map_tribunal, map_ementa):
    lista_unificada = []
    df = df.fillna("")
    
    for _, row in df.iterrows():
        ementa = str(row.get(map_ementa, "")).strip()
        if not ementa or len(ementa) < 50:
            continue
            
        documento = {
            "id_unico": str(uuid.uuid4()),
            "fonte": fonte_nome,
            "processo": str(row.get(map_processo, "N/A")),
            "tribunal": str(row.get(map_tribunal, "Desconhecido")),
            "texto": ementa
        }
        lista_unificada.append(documento)
        
    return lista_unificada

def extrair_repojus(tribunal, limit=1000):
    if not load_dataset:
        return []
        
    print(f"Baixando {limit} registros de {tribunal.upper()}...")
    try:
        dataset_hf = load_dataset("andrebadini/repojus", name=f"tribunal-{tribunal}", split=f"train[:{limit}]", token=os.environ.get("HF_TOKEN"))
        df_hf = dataset_hf.to_pandas()
    except Exception as e:
        print(f"⚠️ Falha ({e}). Usando Reserva...")
        try:
            parquet_path = os.path.join(DATA_DIR, f"{tribunal}_reserva.parquet")
            df_hf = pd.read_parquet(parquet_path)
        except Exception:
            return []
            
    return padronizar_dados(f"HuggingFace_{tribunal.upper()}", df_hf, "processo", "tribunal", "ementa")

def chunker(seq, size):
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))

def rodar_pipeline_etl(batch_limit=5000):
    print(f"🚀 Iniciando Pipeline ETL Acelerado por Hardware (Lote de {batch_limit} por Tribunal)...")
    
    dados_stj = extrair_repojus("stj", limit=batch_limit)
    dados_tjsp = extrair_repojus("tjsp", limit=batch_limit)
    
    dados_unificados = dados_stj + dados_tjsp
    total = len(dados_unificados)
    print(f"📦 Total de registros unificados prontos para injeção: {total}")
    
    if not dados_unificados:
        return
        
    batch_size = 500
    
    print(f"⚡ Iniciando vetorização matricial usando MPS (Apple Silicon GPU) em blocos de {batch_size}...")
    
    for i, lote in enumerate(chunker(dados_unificados, batch_size)):
        print(f"Processando Bloco {i+1}/{(total//batch_size)+1}...")
        
        textos = [doc["texto"] for doc in lote]
        ids = [doc["id_unico"] for doc in lote]
        metadados = [{"fonte_origem": doc["fonte"], "processo": doc["processo"], "tribunal": doc["tribunal"]} for doc in lote]
        
        # 1. Geração Matricial via MPS
        vetores = gerar_embeddings_em_lote(textos, batch_size=256)
        
        # 2. Inserção em Bloco no ChromaDB
        collection.add(
            ids=ids,
            embeddings=vetores,
            documents=textos,
            metadatas=metadados
        )
        
    print(f"✅ ETL Batch Concluído! Acervo vetorizado com velocidade máxima.")

if __name__ == "__main__":
    rodar_pipeline_etl(batch_limit=2500)  # 2500 STJ + 2500 TJSP = 5000 total
