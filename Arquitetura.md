# Arquitetura Ovid.IA (Atualizada)

Abaixo está o diagrama completo de como os componentes do Ovid.IA estão interligados após as nossas últimas atualizações (Motor Determinístico de Prazos e Pipeline ETL para RAG).

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
    end

    %% Backend
    subgraph BACKEND ["API Gateway (FastAPI)"]
        Router_Auditoria[/contratos/analisar/]
        Router_Prazos[/prazos/extrair/]
        Router_RAG[/jurisprudencia/buscar/]
        
        Parser[Motor OCR / PDFPlumber]
        Calculadora[Motor Determinístico de Prazos - Datetime]
    end

    %% Motores de IA (100% Locais)
    subgraph AI_MOTORES ["Motores Locais (Air-Gap)"]
        Ollama[Ollama - Hermes3:8b]
        LangTool[LanguageTool - Revisão Gramatical]
        Embeddings[Sentence-Transformers - all-MiniLM]
    end

    %% Bancos de Dados
    subgraph DATABASE ["Persistência de Dados"]
        ChromaDB[(ChromaDB - Banco Vetorial)]
    end

    %% ETL Externo
    subgraph ETL ["Pipeline ETL de Dados (Script Offline)"]
        ETL_Script[etl_jurisprudencia.py]
        Schema_Mapper{Schema Mapper}
    end

    %% Fontes Externas
    Kaggle[(CSV Kaggle - Força Bruta)]:::external
    HF[(Hugging Face - Acadêmico)]:::external

    %% Conexões do Usuário
    User -->|Arrasta PDF| UI_Auditoria
    User -->|Arrasta Intimação| UI_Prazos
    User -->|Pesquisa Tese| UI_RAG

    %% Conexões Frontend -> Backend
    UI_Auditoria -->|POST| Router_Auditoria
    UI_Prazos -->|POST| Router_Prazos
    UI_RAG -->|POST| Router_RAG

    %% Conexões Auditoria
    Router_Auditoria -->|Extrai Texto| Parser
    Parser -->|Contexto| Ollama
    Parser -->|Verifica Ortografia| LangTool

    %% Conexões Prazos (Cérebro Híbrido)
    Router_Prazos -->|1. Pede Datas (NER)| Ollama
    Ollama -.->|Retorna Prazo Bruto| Router_Prazos
    Router_Prazos -->|2. Injeta no Algoritmo| Calculadora
    Calculadora -.->|Data Fatal (Pula FDS)| UI_Prazos

    %% Conexões ETL e RAG
    Kaggle -->|Download| ETL_Script
    HF -->|Download API| ETL_Script
    ETL_Script --> Schema_Mapper
    Schema_Mapper -->|Textos Padronizados| Embeddings
    Embeddings -->|Vetores 384d| ChromaDB

    Router_RAG -->|1. Converte Pergunta| Embeddings
    Embeddings -.->|Vetor da Pergunta| Router_RAG
    Router_RAG -->|2. Busca Semântica| ChromaDB
    ChromaDB -.->|Top 3 Ementas| Router_RAG
    Router_RAG -->|3. Injeta Contexto| Ollama
    Ollama -.->|Parecer Jurídico| UI_RAG

    %% Aplicação de Estilos
    UI_Auditoria,UI_Prazos,UI_RAG class frontend;
    Router_Auditoria,Router_Prazos,Router_RAG,Parser,Calculadora class backend;
    Ollama,LangTool,Embeddings class ia;
    ChromaDB class db;
    ETL_Script,Schema_Mapper class backend;

```
