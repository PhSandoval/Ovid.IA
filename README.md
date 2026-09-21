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
- **Local:** `backend/`
- **Componentes:**
  - `app/main.py`: O roteador (API Gateway). Gerencia os endpoints, orquestra os serviços e garante validação via Pydantic.
  - `app/schemas.py`: Modelos de dados. Garantem que a IA não retorne textos soltos, forçando saídas em JSON estruturado (ex: `ResumoAuditoria`, `ResumoAutos`).
  - `app/services/parser.py`: Motor OCR e leitura de textos de PDFs usando `pdfplumber`.
  - `app/services/vector_db.py`: Banco de dados vetorial (`ChromaDB`). Transforma jurisprudência em matemática para busca por similaridade semântica.
  - `app/services/prazos.py`: Motor lógico-matemático. Pega a quantidade de dias lida pela IA e faz a contagem de dias úteis segundo o CPC, devolvendo a data fatal sem alucinações.
  - **Ollama**: Roda em background, fornecendo o LLM (`hermes3:8b`) que atua como o "cérebro" para estruturar informações.

## 🚀 Módulos (Sprints)

### 1. Auditoria de Contratos (`/contratos/analisar`)
O **Módulo 1** é projetado para atuar como um "Classificador de Risco" automatizado para minutas e contratos recebidos pelo escritório.
- **Como funciona:** O advogado faz o upload de um PDF no frontend (Streamlit). O FastAPI recebe o documento e usa a biblioteca `pdfplumber` para realizar um "extrator a frio" (lendo apenas a camada de texto, ignorando imagens maliciosas). Esse texto é então encapsulado em um *Prompt de Sistema* extremamente restrito (`temperature=0.0`) e enviado ao motor local Ollama (`hermes3:8b`). A IA tem permissão **apenas** para identificar cláusulas abusivas e devolver um JSON estrito (tipado via Pydantic).
- **🔒 Segurança e Conformidade (LGPD):** 
  Neste módulo (e em todo o sistema Ovid.IA), a segurança da informação é o pilar central. Contratos jurídicos possuem dados hipersensíveis (valores financeiros, nomes de partes, CNPJs). O diferencial do Ovid.IA é o isolamento em *Air-Gap Lógico*:
  - **Zero Nuvem:** Absolutamente NENHUM dado (PDF, texto ou metadado) é enviado para APIs externas como OpenAI, Google ou Anthropic. Toda a inferência de IA ocorre usando a placa gráfica (ou processador) da própria máquina onde o servidor está rodando, garantindo 100% de sigilo sob as diretrizes da LGPD e Estatuto da Advocacia.
  - **Prevenção de Alucinação:** Ao forçar o formato JSON e setar a "criatividade" da IA para zero, impedimos que o sistema invente riscos ou vaze dados de contratos de outros clientes nos resultados gerados.

### 2. Busca de Jurisprudência e RAG (`/jurisprudencia/buscar`)
Motor de Geração Aumentada por Recuperação (RAG) para teses jurídicas. O sistema opera em duas vias de arquitetura:
- **🔒 Acervo Local (ChromaDB):** O advogado pode colar ementas no frontend, que são vetorizadas via `Sentence-Transformers` (`all-MiniLM-L6-v2`) e armazenadas localmente no banco ChromaDB. Buscas subsequentes calculam a distância semântica e injetam as ementas no contexto do LLM.
- **☁️ RAG Invertido (API Externa - Escavador):** Endpoint `/jurisprudencia/buscar_externo` integrado com a API Oficial do Escavador para consumir precedentes atualizados da nuvem.
  - **⚠️ Decisão de Arquitetura (Web Scraping banido):** O Ovid.IA não utiliza bibliotecas amadoras de raspagem web (ex: `duckduckgo-search`). Buscadores genéricos retornam "Snippets" mutilados que causam alucinação grave.
  - **Solução Corporativa:** A rota externa utiliza as Chaves de API do **Escavador** para puxar dados em formato JSON estruturado, servindo de base sólida para a geração da IA.

### 3. Resumo de Autos (`/autos/resumir`)
Faz o "Intake" de novos casos. Processa petições iniciais ou autos extensos e extrai instantaneamente as partes (autor/réu), o valor da causa, pedidos formulados, pedidos de tutela e produz um resumo dos fatos.
- **Exportação Corporativa (.DOCX):** Uma das funcionalidades de maior valor para o escritório! Após a análise do "Intake", o sistema permite a exportação do resultado com um único clique para um documento Word (`.docx`) já pré-formatado. Isso elimina o copia-e-cola e acelera o fluxo de peticionamento e elaboração de pareceres internos.

### 4. Revisão Gramatical (`/contratos/revisar_gramatica`)
O **Módulo Fantasma** agora oficializado! Focado exclusivamente no refino ortográfico e coesão textual de peças jurídicas.
- **Como funciona:** Analisa contratos e petições varrendo por erros gramaticais, sugerindo correções fundamentadas nas regras da língua portuguesa e avaliando a clareza e o tom do documento. Essencial para o polimento final antes do protocolo.

### 5. Gestão de Prazos (`/prazos/extrair`)
O **Módulo de Prazos Processuais** introduz o conceito de **Cérebro Híbrido** no Ovid.IA (IA Generativa + Algoritmo Determinístico).
- **O Problema da IA com Datas:** LLMs não têm a capacidade de contar dias úteis num calendário, identificar feriados ou pular finais de semana, sofrendo de altíssimas taxas de "alucinação" matemática.
- **A Solução (Cérebro Híbrido):** 
  - **1º Passo (NER - Inteligência):** A IA atua **exclusivamente** como uma Extratora de Entidades (NER). Ela lê a intimação e "pesca" a Data de Publicação e o Prazo Bruto (ex: `15`).
  - **2º Passo (Motor Determinístico):** O código Python (backend) toma a frente, utilizando a biblioteca nativa `datetime`. Ele adiciona 1 dia ao prazo de início e itera num laço `while`, avançando o relógio temporal e pulando matematicamente os Sábados e Domingos até alcançar os `15` dias exigidos.

## ⚙️ Como Executar

### 1. Requisitos
- Python 3.12 ou superior
- Ollama instalado e rodando com o modelo `hermes3:8b`.

### 2. Rodando o Backend (FastAPI)
```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

### 3. Rodando o Frontend (Streamlit)
Em um **novo terminal** na raiz do projeto:
```bash
source backend/.venv/bin/activate
streamlit run frontend/app.py
```
