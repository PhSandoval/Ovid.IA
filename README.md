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
- **☁️ RAG Invertido (API Externa):** Endpoint `/jurisprudencia/buscar_externo` projetado para consumir precedentes da nuvem (via API) sem vazar os dados sensíveis do escritório.
  - **⚠️ Decisão de Arquitetura (Web Scraping banido):** O Ovid.IA não utiliza bibliotecas amadoras de raspagem web (ex: `duckduckgo-search`). Buscadores genéricos retornam "Snippets" (textos mutilados de 160 caracteres). Injetar trechos cortados pela metade na memória da IA viola o princípio *Garbage In, Garbage Out* e causa alucinação grave (mesmo com `temperature=0.0`), pois o modelo julgará com base em premissas incompletas. Além disso, raspagem sofre *Shadowban* de IP em dias.
  - **Solução Corporativa:** A rota de busca externa encontra-se estruturada como um *Placeholder* preparado exclusivamente para receber integrações sólidas e em formato JSON estruturado, via Chaves de API Oficiais (API Pública do **Datajud/CNJ** ou API Oficial **Jusbrasil/Escavador**).
3. **Resumo de Autos** (`/autos/resumir`):
   Faz o "Intake". Processa petições longas e extrai autor, réu, valor da causa e resumo dos fatos.
### 5. Gestão de Prazos (`/prazos/extrair`)
O **Módulo de Prazos Processuais** introduz o conceito de **Cérebro Híbrido** no Ovid.IA (IA Generativa + Algoritmo Determinístico).
- **O Problema da IA com Datas:** LLMs não têm a capacidade de contar dias úteis num calendário, identificar feriados ou pular finais de semana, sofrendo de altíssimas taxas de "alucinação" matemática.
- **A Solução (Cérebro Híbrido):** 
  - **1º Passo (NER - Inteligência):** A IA atua **exclusivamente** como uma Extratora de Entidades (NER). Ela lê a intimação e "pesca" a Data de Publicação e o Prazo Bruto (ex: `15`).
  - **2º Passo (Motor Determinístico):** O código Python (backend) toma a frente, utilizando a biblioteca nativa `datetime`. Ele adiciona 1 dia ao prazo de início e itera num laço `while`, avançando o relógio temporal e pulando matematicamente os Sábados e Domingos até alcançar os `15` dias exigidos.
- **Exemplo de Cálculo (Pular Finais de Semana):**
  Uma intimação com Data de Publicação em **15/09/2026** (Terça-feira), exigindo **15 dias de prazo** (ex: Impugnação a Laudo Pericial).
  - O prazo inicia no dia 16/09 (D+1).
  - O sistema ignora os Sábados (19/09, 26/09, 03/10) e Domingos (20/09, 27/09, 04/10).
  - Resultado final matemático cravado: **06/10/2026 (Terça-feira)**. Zero margem de alucinação.

## ⚙️ Como Executar

### 1. Requisitos
- Python 3.12 (Recomendado)
- Ollama instalado e rodando com o modelo `hermes3:8b`.

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
