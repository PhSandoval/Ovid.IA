# Ovid.IA - Copiloto Jurídico 100% Local ⚖️🤖

Ovid.IA é um assistente jurídico (LegalTech) focado em privacidade estrita de dados (LGPD). Toda a inferência de IA e processamento de documentos ocorre **localmente**, sem o uso de APIs na nuvem.

## 🏗️ Arquitetura do Sistema

O projeto adota uma arquitetura em duas camadas (Frontend e Backend) fracamente acopladas, comunicando-se via REST.

### 1. Frontend (Streamlit)
Responsável pela interface com o advogado.
- **Local:** `frontend/app.py`
- **Função:** Captura inputs (upload de PDFs, textos), faz chamadas HTTP para o backend local e renderiza os JSONs de resposta em painéis amigáveis.

### 2. Backend (FastAPI + Ollama)
O motor central do sistema.
- **Local:** `ovid_ia_backend/`
- **Componentes:**
  - `app/main.py`: O roteador (API Gateway). Gerencia os endpoints, orquestra os serviços e garante validação via Pydantic.
  - `app/schemas.py`: Modelos de dados. Garantem que a IA não retorne textos soltos, forçando saídas em JSON estruturado (ex: `ResumoAuditoria`, `ResumoAutos`).
  - `app/services/parser.py`: Motor OCR e leitura de textos de PDFs usando `pdfplumber`.
  - `app/services/vector_db.py`: Banco de dados vetorial (`ChromaDB`). Transforma jurisprudência em matemática para busca por similaridade semântica.
  - `app/services/prazos.py`: Motor lógico-matemático. Pega a quantidade de dias lida pela IA e faz a contagem de dias úteis segundo o CPC, devolvendo a data fatal sem alucinações.
  - **Ollama**: Roda em background, fornecendo o LLM (`llama3.1`) que atua como o "cérebro" para estruturar informações.

## 🚀 Módulos (Sprints)

1. **Auditoria de Contratos** (`/contratos/analisar`):
   Lê PDFs e mapeia cláusulas de risco (abusivas, desproporcionais).
2. **Busca de Jurisprudência** (`/jurisprudencia/indexar` e `/jurisprudencia/buscar`):
   Motor RAG. Recebe uma tese e recupera precedentes locais semanticamente próximos usando embeddings.
3. **Resumo de Autos** (`/autos/resumir`):
   Faz o "Intake". Processa petições longas e extrai autor, réu, valor da causa e resumo dos fatos.
4. **Estilometria e Redação** (`/estilometria/gerar`):
   Escreve peças mimetizando o estilo e o vocabulário de sentenças e petições passadas.
5. **Gestão de Prazos (Diário Oficial)** (`/diario-oficial/triar`):
   O LLM identifica a intimação e o número de dias. O Python puro processa a matemática do CPC.

## ⚙️ Como Executar

### 1. Requisitos
- Python 3.12 (Recomendado)
- Ollama instalado e rodando com o modelo `llama3.1`.

### 2. Rodando o Backend
```bash
cd ovid_ia_backend
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

### 3. Rodando o Frontend
Em um **novo terminal**:
```bash
source ovid_ia_backend/.venv/bin/activate
streamlit run frontend/app.py
```
