from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
import pdfplumber
import ollama
import json

app = FastAPI(title="Ovid.IA Backend", version="1.0.0")

class AlertaRisco(BaseModel):
    nivel_risco: str
    clausula: str
    descricao: str
    justificativa_legal: str
    recomendacao: str

class ResumoAuditoria(BaseModel):
    nivel_risco_geral: str
    numero_alertas: int
    alertas: list[AlertaRisco]

@app.post("/contratos/analisar", response_model=ResumoAuditoria)
async def analisar_contrato(file: UploadFile = File(...)):
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Apenas arquivos PDF são suportados neste endpoint.")

    # 1. Extração do Texto via pdfplumber
    texto_contrato = ""
    try:
        with pdfplumber.open(file.file) as pdf:
            for page in pdf.pages:
                extracted = page.extract_text()
                if extracted:
                    texto_contrato += extracted + "\n"
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao extrair texto do PDF: {str(e)}")

    if not texto_contrato.strip():
        raise HTTPException(status_code=400, detail="O PDF parece estar vazio ou é uma imagem sem OCR.")

    # 2. Prompting Sistemático (Engenharia de Prompt para o Llama 3.1)
    system_prompt = """
Você é um advogado especialista em compliance e auditoria de contratos no Brasil.
Sua missão é analisar o texto do contrato fornecido e identificar cláusulas abusivas, penalidades desproporcionais e ausência de termos obrigatórios ou foros inadequados.

Você deve responder ESTRITAMENTE em formato JSON puro, sem nenhum markdown ou texto antes/depois, utilizando EXATAMENTE a seguinte estrutura (schema):

{
  "nivel_risco_geral": "ALTO", // Escolha apenas entre: BAIXO, MÉDIO, ALTO, EXTREMO
  "numero_alertas": 1,
  "alertas": [
    {
      "nivel_risco": "Risco Extremo", // Escolha entre: Atenção, Risco Médio, Risco Alto, Risco Extremo
      "clausula": "Nome ou número da Cláusula",
      "descricao": "O que está errado nesta cláusula e por que é abusiva",
      "justificativa_legal": "Base legal para o apontamento (ex: Código de Defesa do Consumidor, Código Civil)",
      "recomendacao": "Como alterar a redação para mitigar o risco"
    }
  ]
}
"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Analise o seguinte contrato:\n\n{texto_contrato}"}
    ]

    # 3. Chamada para o Ollama (Instância Local - localhost:11434)
    try:
        # A chamada bloqueante local. Em um ambiente de produção pesado, 
        # poderíamos usar AsyncClient do ollama.
        response = ollama.chat(
            model='llama3.1', # ou qwen2.5 dependendo da máquina
            messages=messages,
            format='json',    # Força a saída em JSON estruturado
            options={"temperature": 0.1} # Temperatura baixíssima para evitar alucinação criativa
        )
        
        # 4. Parsing e Validação da Saída
        json_resposta = json.loads(response['message']['content'])
        resultado = ResumoAuditoria(**json_resposta) # Validação estrita do Pydantic
        
        return resultado

    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="O Llama 3.1 não retornou um JSON válido.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na inferência local com Ollama: {str(e)}")
