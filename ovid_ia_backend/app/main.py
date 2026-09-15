from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
import logging
import time

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)
import uuid
from typing import List, Dict, Any
from datetime import date

from app.schemas import (
    ResumoAuditoria, AlertaRisco, DocumentoIndexacao, ResultadoBusca,
    ResumoAutos, RequisicaoRedacao, RespostaRedacao,
    PublicacaoDO, AlertaPrazo, ResultadoTriagem
)
import ollama
import json
from app.services.parser import extrair_texto_pdf
from app.services.vector_db import adicionar_documento, buscar_similaridade
from app.services.prazos import calcular_prazo_fatal

app = FastAPI(
    title="Ovid.IA Backend", 
    description="API para o Módulo de Auditoria de Contratos e Serviços Jurídicos",
    version="1.0.0"
)

@app.post("/contratos/analisar", response_model=ResumoAuditoria)
async def analisar_contrato(arquivo: UploadFile = File(...)) -> ResumoAuditoria:
    """
    Endpoint (Sprint 1) para analisar contratos em formato PDF.
    Extrai o texto do PDF e retorna um payload validado contendo os riscos mapeados.
    """
    start_time = time.time()
    logger.info(f"Iniciando análise de contrato: {arquivo.filename}")
    
    if not arquivo.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Apenas arquivos PDF são aceitos.")

    try:
        texto = await extrair_texto_pdf(arquivo)
    except Exception as e:
        logger.error(f"Erro extraindo texto: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao processar PDF: {str(e)}")

    if not texto.strip():
        raise HTTPException(status_code=400, detail="O documento parece estar vazio ou não possui OCR legível.")

    system_prompt = """
Você é um advogado especialista em compliance e auditoria de contratos.
Analise o texto do contrato fornecido e identifique cláusulas abusivas, penalidades desproporcionais e ausência de termos obrigatórios.
Você deve responder ESTRITAMENTE em formato JSON, utilizando a seguinte estrutura:

{
  "nivel_risco_geral": "ALTO",
  "total_alertas": 1,
  "alertas": [
    {
      "nivel_risco": "Risco Extremo",
      "clausula": "Nome ou número da Cláusula",
      "descricao_risco": "O que está errado nesta cláusula",
      "recomendacao": "Como alterar a redação"
    }
  ]
}
"""
    try:
        response = ollama.chat(
            model='llama3.1',
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": texto}
            ],
            format='json',
            options={"temperature": 0.0}
        )
        json_resp = json.loads(response['message']['content'])
        
        # Garantir que o nome do arquivo seja injetado
        if "nome_arquivo" not in json_resp:
            json_resp["nome_arquivo"] = arquivo.filename
            
        resumo = ResumoAuditoria(**json_resp)
        logger.info(f"Análise concluída em {time.time() - start_time:.2f}s")
        return resumo
    except Exception as e:
        logger.error(f"Erro na inferência: {e}")
        raise HTTPException(status_code=500, detail=f"Erro na inferência do Ollama: {str(e)}")

# --- MÓDULO 2: Busca de Jurisprudência (Motor RAG Local) ---

@app.post("/jurisprudencia/indexar", response_model=Dict[str, Any])
async def indexar_jurisprudencia(doc: DocumentoIndexacao):
    """
    Endpoint para vetorizar e salvar jurisprudência no banco local ChromaDB.
    Recebe um texto e seus metadados (como número do processo, tribunal).
    """
    id_unico = str(uuid.uuid4())
    try:
        adicionar_documento(id_doc=id_unico, texto=doc.texto, metadados=doc.metadados)
        return {
            "status": "sucesso", 
            "id_documento": id_unico, 
            "mensagem": "Documento indexado com sucesso no ChromaDB local."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao indexar documento: {str(e)}")

class QueryBusca(BaseModel):
    query: str

@app.post("/jurisprudencia/buscar", response_model=List[ResultadoBusca])
async def buscar_jurisprudencia(busca: QueryBusca):
    """
    Recebe uma query (tese do advogado), converte em embedding e busca os 3 resultados 
    mais semanticamente próximos na base vetorial local.
    """
    try:
        resultados = buscar_similaridade(query=busca.query, limite=3)
        return resultados
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar jurisprudência: {str(e)}")

# --- MÓDULO 3: Resumo de Autos ---

@app.post("/autos/resumir", response_model=ResumoAutos)
async def resumir_autos(arquivo: UploadFile = File(...)):
    """
    Recebe um arquivo PDF (autos processuais), extrai o texto e usa o Ollama 
    para estruturar os dados chave em JSON.
    """
    if not arquivo.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Apenas arquivos PDF são aceitos.")

    try:
        texto = await extrair_texto_pdf(arquivo)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao ler PDF: {str(e)}")

    if not texto.strip():
        raise HTTPException(status_code=400, detail="PDF vazio.")

    system_prompt = """
Você é um assistente jurídico. Leia a petição inicial e extraia ESTRITAMENTE em formato JSON:
{
  "parte_autora": "Nome do Autor",
  "parte_re": "Nome do Réu",
  "valor_causa": 0.00,
  "natureza_acao": "Tipo de Ação",
  "sintese_fatos": "Resumo em um parágrafo",
  "proximo_prazo": "Qualquer prazo citado ou 'Não identificado'"
}
"""
    try:
        response = ollama.chat(
            model='llama3.1',
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": texto}
            ],
            format='json',
            options={"temperature": 0.0}
        )
        json_resp = json.loads(response['message']['content'])
        return ResumoAutos(**json_resp)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na inferência do Ollama: {str(e)}")

# --- MÓDULO 4: Redação e Estilometria ---

@app.post("/estilometria/gerar", response_model=RespostaRedacao)
async def gerar_redacao(req: RequisicaoRedacao):
    """
    Usa o RAG local para buscar precedentes parecidos e pede ao Ollama 
    para gerar uma nova peça no estilo adequado.
    """
    # 1. Recuperar contexto (precedentes do banco vetorial)
    precedentes = buscar_similaridade(query=req.fatos_brutos, limite=2)
    textos_referencia = "\n\n".join([p["texto_recuperado"] for p in precedentes])

    system_prompt = f"""
Você é um advogado sênior escrevendo uma peça processual.
Siga EXATAMENTE o estilo, tom de voz e formatação dos precedentes abaixo.

PRECEDENTES (Use como base de estilo):
{textos_referencia}

INSTRUÇÕES:
- Tipo de peça: {req.tipo_peca}
- Tom desejado: {req.tom_desejado}
- Fatos: {req.fatos_brutos}
"""
    try:
        response = ollama.chat(
            model='llama3.1',
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "Por favor, redija a peça."}
            ],
            options={"temperature": 0.0}
        )
        
        return RespostaRedacao(texto_gerado=response['message']['content'])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar redação: {str(e)}")

# --- MÓDULO 5: Diário Oficial e Prazos ---

class LLMExtracaoPrazo(BaseModel):
    """Schema temporário apenas para parsear o JSON do LLM antes da matemática."""
    numero_processo: str
    tipo_ato_judicial: str
    dias_prazo: int
    criticidade: str

@app.post("/diario-oficial/triar", response_model=ResultadoTriagem)
async def triar_publicacoes_do(pub: PublicacaoDO):
    """
    Recebe um texto do Diário Oficial. 
    Usa o Ollama APENAS para Extração de Entidades (NER).
    A matemática da data fatal é calculada localmente no Python via CPC.
    """
    system_prompt = """
Você é um leitor de Diário Oficial especializado em extração de entidades.
Leia a publicação e retorne ESTRITAMENTE um JSON com as entidades extraídas.
NÃO FAÇA CONTAS MATEMÁTICAS.
{
  "numero_processo": "0000000-00.0000.0.00.0000",
  "tipo_ato_judicial": "Ato identificado (ex: Intimação para Contestação)",
  "dias_prazo": 15, // O NÚMERO EXATO DE DIAS CITADO NO TEXTO (em inteiro)
  "criticidade": "ALTA" // Escolha entre: BAIXA, MÉDIA, ALTA, URGENTE
}
"""
    try:
        response = ollama.chat(
            model='llama3.1',
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": pub.texto_publicacao}
            ],
            format='json',
            options={"temperature": 0.0}
        )
        
        json_resp = json.loads(response['message']['content'])
        dados_llm = LLMExtracaoPrazo(**json_resp)
        
        # O Motor Matemático Roda no Python (Seguro e sem Alucinações)
        data_fatal_calculada = calcular_prazo_fatal(
            data_publicacao=pub.data_publicacao,
            dias_uteis=dados_llm.dias_prazo
        )
        
        alerta = AlertaPrazo(
            numero_processo=dados_llm.numero_processo,
            tipo_ato_judicial=dados_llm.tipo_ato_judicial,
            dias_prazo=dados_llm.dias_prazo,
            data_fatal=data_fatal_calculada,
            criticidade=dados_llm.criticidade
        )
        
        return ResultadoTriagem(alertas=[alerta])

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na triagem de prazo: {str(e)}")
