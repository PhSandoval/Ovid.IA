# Arquitetura Ovid.IA (Atualizada - Versão Final)

Abaixo está o diagrama completo de como os componentes do Ovid.IA estão interligados após as implementações finais (Intake Estruturado, RAG com Qwen 2.5 3B e Streaming).

```mermaid
graph TD
    %% Cores e Estilos
    classDef frontend fill:#4CAF50,stroke:#388E3C,stroke-width:2px,color:white;
    classDef backend fill:#2196F3,stroke:#1976D2,stroke-width:2px,color:white;
    classDef ia fill:#9C27B0,stroke:#7B1FA2,stroke-width:2px,color:white;
    classDef db fill:#FF9800,stroke:#F57C00,stroke-width:2px,color:white;
    classDef external fill:#607D8B,stroke:#455A64,stroke-width:2px,color:white;

    %% Atores
    User((Advogado))

    %% Frontend
    subgraph FRONTEND ["Interface do Usuário (Streamlit)"]
        UI_Auditoria[Auditoria de Contratos]
        UI_Prazos[Gestão de Prazos]
        UI_RAG[Busca de Jurisprudência]
        UI_Intake[Resumo de Autos]
        UI_Padronizacao[Módulo de Padronização de Peças]
    end

    %% Backend
    subgraph BACKEND ["API Gateway (FastAPI)"]
        Router_Auditoria[/contratos/analisar/]
        Router_Prazos[/prazos/extrair/]
        Router_RAG[/jurisprudencia/buscar/]
        Router_Intake[/autos/resumir/]
        Router_Padronizacao[/pecas/gerar/]
        
        Parser[Motor OCR / PDFPlumber]
        Calculadora[Motor Determinístico - Datas]
    end

    %% Motores de IA (100% Locais)
    subgraph AI_MOTORES ["Motores Locais (Air-Gap)"]
        Ollama_Hermes[Ollama - Hermes 3 8B]
        Ollama_Qwen[Ollama - Qwen 2.5 3B]
        LangTool[LanguageTool - Gramática]
        Embeddings[Sentence-Transformers - all-MiniLM]
    end

    %% Bancos de Dados
    subgraph DATABASE ["Persistência de Dados"]
        ChromaDB[(ChromaDB - Banco Vetorial)]
    end

    %% ETL Externo
    subgraph ETL ["Pipeline ETL (Segurança Anti-Apagão)"]
        ETL_Jurisprudencia["etl_jurisprudencia.py (HF)"]
        ETL_Acervo["ETL Acervo Interno (Scripts 01 e 02)"]
        Parquet_Fallback[(Backup Local .parquet)]
    end

    %% Fontes Externas
    HF[(Hugging Face - Repojus)]:::external
    AcervoLocal[(Arquivos Locais - Acervo_Clientes)]:::external

    %% Conexões do Usuário
    User -->|PDF Contrato| UI_Auditoria
    User -->|PDF Intimação| UI_Prazos
    User -->|Tese Jurídica| UI_RAG
    User -->|PDF Inicial| UI_Intake
    User -->|Pedido de Peça| UI_Padronizacao

    %% Conexões Frontend -> Backend
    UI_Auditoria -->|"POST (Stream)"| Router_Auditoria
    UI_Prazos -->|POST| Router_Prazos
    UI_RAG -->|"POST (Stream)"| Router_RAG
    UI_Intake -->|POST| Router_Intake
    UI_Padronizacao -->|"POST (Agentic Loop)"| Router_Padronizacao

    %% Conexões Intake (Novo)
    Router_Intake -->|Lê PDF Inteiro| Parser
    Parser -->|Contexto Bruto| Ollama_Hermes
    Ollama_Hermes -.->|JSON Estruturado| UI_Intake

    %% Conexões Padronização (Agentic Workflow)
    Router_Padronizacao -->|Filtro Metadado| ChromaDB
    ChromaDB -.->|Molde Padrão Ouro| Router_Padronizacao
    Router_Padronizacao <-->|Loop Circuit Breaker| Ollama_Hermes
    Ollama_Hermes -.->|DOCX Final| UI_Padronizacao

    %% Conexões Auditoria
    Router_Auditoria -->|Lotes/Overlap| Parser
    Parser -->|Contexto Loteado| Ollama_Hermes
    Parser -->|Verifica Ortografia| LangTool

    %% Conexões Prazos
    Router_Prazos -->|Pede Metadados| Ollama_Hermes
    Ollama_Hermes -.->|Prazo Bruto| Router_Prazos
    Router_Prazos -->|Injeta no Algoritmo| Calculadora
    Calculadora -.->|"Data Fatal (Pula FDS)"| UI_Prazos

    %% Conexões ETL e RAG
    HF -->|Download API Oficial| ETL_Jurisprudencia
    AcervoLocal -->|Extração PDF/DOCX| ETL_Acervo
    ETL_Jurisprudencia -->|Falha na Rede| Parquet_Fallback
    ETL_Jurisprudencia -->|Ementas| Embeddings
    ETL_Acervo -->|"Textos + Metadados Ricos (GPU MPS)"| Embeddings
    Embeddings -->|Vetores 384d| ChromaDB

    Router_RAG -->|1. Converte Pergunta| Embeddings
    Embeddings -.->|Vetor da Pergunta| Router_RAG
    Router_RAG -->|2. Busca Semântica| ChromaDB
    ChromaDB -.->|Top 3 Ementas| Router_RAG
    Router_RAG -->|3. Injeta Contexto| Ollama_Qwen
    Ollama_Qwen -.->|Parecer em Streaming| UI_RAG

    %% Aplicação de Estilos
    class UI_Auditoria,UI_Prazos,UI_RAG,UI_Intake,UI_Padronizacao frontend;
    class Router_Auditoria,Router_Prazos,Router_RAG,Router_Intake,Router_Padronizacao,Parser,Calculadora backend;
    class Ollama_Hermes,Ollama_Qwen,LangTool,Embeddings ia;
    class ChromaDB,Parquet_Fallback db;
    class ETL_Jurisprudencia,ETL_Acervo backend;

```
