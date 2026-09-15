from pydantic import BaseModel
from typing import List, Dict, Any

class AlertaRisco(BaseModel):
    """Modelo que representa um alerta de risco encontrado em uma cláusula."""
    nivel_risco: str
    clausula: str
    descricao_risco: str
    recomendacao: str

class ResumoAuditoria(BaseModel):
    """Modelo que consolida todos os alertas de um documento analisado."""
    nome_arquivo: str
    nivel_risco_geral: str
    total_alertas: int
    alertas: List[AlertaRisco]

class DocumentoIndexacao(BaseModel):
    """Modelo para enviar um documento para indexação no motor RAG."""
    texto: str
    metadados: Dict[str, Any]

class ResultadoBusca(BaseModel):
    """Modelo para retornar um resultado de busca semântica."""
    texto_recuperado: str
    score: float
    metadados: Dict[str, Any]

# --- SPRINT 3 SCHEMAS ---

class ResumoAutos(BaseModel):
    """Modelo para extração estruturada de dados de uma petição inicial ou autos."""
    parte_autora: str
    parte_re: str
    valor_causa: float
    natureza_acao: str
    sintese_fatos: str
    proximo_prazo: str

class RequisicaoRedacao(BaseModel):
    """Modelo para a requisição de geração de nova peça jurídica (estilometria)."""
    fatos_brutos: str
    tipo_peca: str
    tom_desejado: str

class RespostaRedacao(BaseModel):
    """Modelo para o retorno da peça redigida pela IA."""
    texto_gerado: str

# --- SPRINT 4 SCHEMAS ---
from datetime import date

class PublicacaoDO(BaseModel):
    texto_publicacao: str
    data_publicacao: date

class AlertaPrazo(BaseModel):
    numero_processo: str
    tipo_ato_judicial: str
    dias_prazo: int
    data_fatal: date
    criticidade: str

class ResultadoTriagem(BaseModel):
    alertas: List[AlertaPrazo]
