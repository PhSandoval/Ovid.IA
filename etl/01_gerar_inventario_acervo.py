import os
import re
import csv
from datetime import datetime

# Diretório alvo
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGET_DIR = os.path.join(BASE_DIR, "Acervo_Clientes")
OUTPUT_CSV = os.path.join(BASE_DIR, "data", "inventario_acervo_interno.csv")

REGEX_CNJ = r"\b\d{7}[-]?\d{2}[.]?(\d{4})[.]?\d[.]?\d{2}[.]?\d{4}\b"

CATEGORIAS = {
    "Contencioso Cível e Tributário": ["ação", "acao", "processo", "impugnação", "notificação", "notificacao", "itbi", "monitória", "monitoria"],
    "Direito Societário e M&A": ["ata", "acordo de propriet", "empresa", "permuta", "quotas", "empreendimentos", "locadora", "jazam"],
    "Direito Imobiliário e Rural": ["sítio", "sitio", "fazenda", "venda", "locação", "locacao", "imóvel", "imovel", "retificação", "iptu"],
    "Planejamento Sucessório e Família": ["inventário", "inventario", "pacto", "doação", "doacao", "sucessório", "sucessorio"],
    "Contratos e Consultivo": ["contrato", "compra e venda", "olam", "blindagem"],
    "Trabalhista": ["trabalhista", "rh"]
}

TIPOS_DOC = {
    "Ata": ["ata "],
    "Contrato Social": ["contrato social"],
    "Distrato": ["distrato"],
    "Acordo de Sócios/Proprietários": ["acordo de propriet", "acordo de sócio"],
    "Contrato/Instrumento": ["contrato", "instrumento"],
    "Petição Inicial": ["ação ", "acao ", "inicial"],
    "Notificação": ["notificação", "notificacao", "pedido de explicações"],
    "Recurso": ["apelação", "agravo", "recurso"],
    "Manifestação/Impugnação": ["manifestação", "impugnação", "manifestacao"],
    "Documento Pessoal/Procuração": ["procuração", "rg", "cnh", "cidadania", "certidão", "pessoal"]
}

def extrair_partes(nome_arquivo):
    # Procura padrões como "A x B", "A vs B", "A - B"
    match = re.search(r"(.+?)\s+(x|vs|-)\s+(.+)", nome_arquivo, flags=re.IGNORECASE)
    if match:
        return f"{match.group(1).strip()} x {match.group(3).split('.')[0].strip()}"
    return "N/A"

def processar_arquivo(root, file):
    caminho_lower = (os.path.basename(root) + " " + file).lower()
    
    # 1. Extração do CNJ e Ano do Documento
    match_cnj = re.search(REGEX_CNJ, caminho_lower)
    cnj = match_cnj.group(0) if match_cnj else "N/A"
    
    # Tenta puxar o ano do CNJ, se não, tenta puxar do texto (ex: 2021, 2022)
    ano_doc = "N/A"
    if match_cnj:
        ano_doc = match_cnj.group(1) # O grupo 1 da regex captura os 4 dígitos do ano do CNJ
    else:
        match_ano = re.search(r"\b(19\d{2}|20\d{2})\b", caminho_lower)
        if match_ano:
            ano_doc = match_ano.group(1)
            
    # 2. Categoria (Macro)
    categoria = "Diversos / Pessoais"
    for cat, keywords in CATEGORIAS.items():
        if any(kw in caminho_lower for kw in keywords):
            categoria = cat
            break
            
    # 3. Tipo do Documento (Granularidade Fina)
    tipo_doc = "Outros"
    for tipo, keywords in TIPOS_DOC.items():
        if any(kw in caminho_lower for kw in keywords):
            tipo_doc = tipo
            break
            
    # 4. Status Padrão Ouro
    padrao_ouro = any(kw in caminho_lower for kw in ["assinado", "final", "protocolado", "homologado", "sentença"])
    
    # 5. Partes Envolvidas
    partes = extrair_partes(file)
    
    return {
        "Nome_Arquivo": file,
        "Caminho_Absoluto": os.path.join(root, file),
        "Categoria": categoria,
        "Tipo_Documento": tipo_doc,
        "Numero_CNJ": cnj,
        "Ano_Documento": ano_doc,
        "Status_Padrao_Ouro": padrao_ouro,
        "Partes_Envolvidas": partes
    }

def rodar_indexacao():
    print("Atualizando ETL com Enriquecimento Avançado de Metadados...")
    registros = []
    
    for root, dirs, files in os.walk(TARGET_DIR):
        for file in files:
            if file.startswith('.') or file.startswith('~'):
                continue
            registros.append(processar_arquivo(root, file))
            
    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
    colunas = ["Nome_Arquivo", "Caminho_Absoluto", "Categoria", "Tipo_Documento", "Numero_CNJ", "Ano_Documento", "Status_Padrao_Ouro", "Partes_Envolvidas"]
    
    with open(OUTPUT_CSV, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=colunas)
        writer.writeheader()
        writer.writerows(registros)
        
    print(f"✅ Sucesso! CSV atualizado com Metadados Profundos (Granularidade, Tempo, Status Ouro e Partes).")

if __name__ == "__main__":
    rodar_indexacao()
