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

### 1. Auditoria de Contratos (`/contratos/analisar`)
O **Módulo 1** é projetado para atuar como um "Classificador de Risco" automatizado para minutas e contratos recebidos pelo escritório.
- **Como funciona:** O advogado faz o upload de um PDF no frontend (Streamlit). O FastAPI recebe o documento e usa a biblioteca `pdfplumber` para realizar um "extrator a frio" (lendo apenas a camada de texto, ignorando imagens maliciosas). Esse texto é então encapsulado em um *Prompt de Sistema* extremamente restrito (`temperature=0.0`) e enviado ao motor local Ollama (`llama3.1`). A IA tem permissão **apenas** para identificar cláusulas abusivas e devolver um JSON estrito (tipado via Pydantic).
- **🔒 Segurança e Conformidade (LGPD):** 
  Neste módulo (e em todo o sistema Ovid.IA), a segurança da informação é o pilar central. Contratos jurídicos possuem dados hipersensíveis (valores financeiros, nomes de partes, CNPJs). O diferencial do Ovid.IA é o isolamento em *Air-Gap Lógico*:
  - **Zero Nuvem:** Absolutamente NENHUM dado (PDF, texto ou metadado) é enviado para APIs externas como OpenAI, Google ou Anthropic. Toda a inferência de IA ocorre usando a placa gráfica (ou processador) da própria máquina onde o servidor está rodando, garantindo 100% de sigilo sob as diretrizes da LGPD e Estatuto da Advocacia.
  - **Prevenção de Alucinação:** Ao forçar o formato JSON e setar a "criatividade" da IA para zero, impedimos que o sistema invente riscos ou vaze dados de contratos de outros clientes nos resultados gerados.

### 2. Busca de Jurisprudência (`/jurisprudencia/indexar` e `/jurisprudencia/buscar`)
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
