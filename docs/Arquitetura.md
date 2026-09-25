# Arquitetura Ovid.IA (Atualizada - Versão Final)

Abaixo está o diagrama completo de como os componentes do Ovid.IA estão interligados após as implementações finais (Intake Estruturado, RAG com Qwen 2.5 3B e Streaming).

```mermaid
graph TD
    %% Estilos
    classDef frontend fill:#4CAF50,stroke:#388E3C,stroke-width:2px,color:white;
    classDef backend fill:#2196F3,stroke:#1976D2,stroke-width:2px,color:white;
    classDef ia fill:#9C27B0,stroke:#7B1FA2,stroke-width:2px,color:white;
    classDef db fill:#FF9800,stroke:#F57C00,stroke-width:2px,color:white;
    classDef cloud fill:#0078D4,stroke:#005A9E,stroke-width:2px,color:white;

    Advogado((Usuário))

    subgraph "Camada de Apresentação"
        UI[Streamlit UI]
    end

    subgraph "Camada Lógica (Stateless)"
        API[FastAPI Gateway]
        ETL_Memory[Parser em Memória - BytesIO]
        QA_CircuitBreaker[QA LLM-as-a-Judge]
    end

    subgraph "Camada de Persistência Híbrida"
        PG[(PostgreSQL + pgvector)]
    end
    
    subgraph "M365 Corporativo"
        GraphAPI[Microsoft Graph API]:::cloud
        OneDrive[(OneDrive Cloud)]:::cloud
    end

    subgraph "IA Local (Air-Gap)"
        Ollama[Ollama - Embeddings & Inference]
    end

    Advogado -->|Busca Peça Padrão| UI
    UI -->|POST /pecas| API
    
    API -->|1. Busca SQL/Vetor| PG
    PG -.->|Retorna item_id| API
    
    API -->|2. MSAL Auth| GraphAPI
    GraphAPI -->|3. Download File Stream| OneDrive
    OneDrive -.->|4. PDF In-Memory| ETL_Memory
    
    ETL_Memory -->|5. Padrão Ouro Completo| Ollama
    Ollama -.->|6. Peça Clonada/Rascunho| QA_CircuitBreaker
    
    QA_CircuitBreaker <-->|7. Loop de Autocorreção (Max 3x)| Ollama
    QA_CircuitBreaker -.->|8. Peça Validada| UI

    class UI frontend;
    class API,ETL_Memory,QA_CircuitBreaker backend;
    class Ollama ia;
    class PG db;
```
