import pandas as pd
import json
import uuid
import os
import sys

# Diretórios principais baseados na nova estrutura do Monorepo
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_DIR = os.path.join(BASE_DIR, "backend")
DATA_DIR = os.path.join(BASE_DIR, "data")

# Adiciona a pasta backend no topo do path para achar o motor do DB
sys.path.insert(0, BACKEND_DIR)

try:
    from datasets import load_dataset
except ImportError:
    print("A biblioteca 'datasets' não está instalada. Execute: pip install datasets pandas")
    load_dataset = None

# Importa o db local do nosso projeto
from app.services.vector_db import collection, adicionar_documento

def padronizar_dados(fonte_nome, df, map_processo, map_tribunal, map_ementa):
    """Transforma qualquer formato num schema unificado"""
    lista_unificada = []
    
    # Preenche NaNs com strings vazias para evitar erros
    df = df.fillna("")
    
    for _, row in df.iterrows():
        ementa = str(row.get(map_ementa, "")).strip()
        
        # Ignora linhas sem ementa
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

from tqdm import tqdm

def extrair_repojus(tribunal, limit=1000):
    """Função genérica para extrair do HF com fallback"""
    if not load_dataset:
        return []
        
    print(f"Tentando baixar {limit} registros de {tribunal} via API...")
    try:
        # Pega a fatia solicitada no split
        dataset_hf = load_dataset("andrebadini/repojus", name=f"tribunal-{tribunal}", split=f"train[:{limit}]", token=os.environ.get("HF_TOKEN"))
        df_hf = dataset_hf.to_pandas()
    except Exception as e:
        print(f"⚠️ Falha na rede ({e}). Ativando Reserva Offline...")
        try:
            parquet_path = os.path.join(DATA_DIR, f"{tribunal}_reserva.parquet")
            df_hf = pd.read_parquet(parquet_path)
            print(f"✅ Leitura Offline do {tribunal} bem-sucedida!")
        except Exception as e2:
            print(f"❌ Falha: Arquivo '{tribunal}_reserva.parquet' não encontrado.")
            return []
            
    return padronizar_dados(
        fonte_nome=f"HuggingFace_{tribunal.upper()}",
        df=df_hf,
        map_processo="processo", 
        map_tribunal="tribunal",  
        map_ementa="ementa"
    )

def rodar_pipeline_etl(batch_limit=1000):
    print(f"Iniciando Pipeline ETL Larga Escala (Lote de {batch_limit} por Tribunal)...")
    
    # 1. EXTRACT & TRANSFORM
    dados_stj = extrair_repojus("stj", limit=batch_limit)
    dados_tjsp = extrair_repojus("tjsp", limit=batch_limit)
    
    dados_unificados = dados_stj + dados_tjsp
    print(f"Total de registros unificados prontos para injeção: {len(dados_unificados)}")
    
    if not dados_unificados:
        return
        
    # 2. LOAD (Injeção no ChromaDB com Barra de Progresso)
    print("Iniciando vetorização...")
    
    for doc in tqdm(dados_unificados, desc="Gerando Embeddings e Salvando no ChromaDB"):
        metadados = {
            "fonte_origem": doc["fonte"],
            "processo": doc["processo"],
            "tribunal": doc["tribunal"]
        }
        adicionar_documento(texto=doc["texto"], metadados=metadados)
        
    print(f"✅ ETL Batch Concluído! Acervo vetorizado com sucesso.")

if __name__ == "__main__":
    rodar_pipeline_etl(batch_limit=1000)
