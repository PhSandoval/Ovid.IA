import streamlit as st
import pandas as pd
import time

# Configuração da página - deve ser a primeira chamada Streamlit
st.set_page_config(
    page_title="Ovid.IA",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização customizada básica
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #004085;
        color: white;
    }
    .stButton>button:hover {
        background-color: #0056b3;
        color: white;
    }
    .title-text {
        color: #004085;
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 700;
    }
    .subtitle-text {
        color: #6c757d;
        font-family: 'Helvetica Neue', sans-serif;
    }
    </style>
""", unsafe_allow_html=True)

def render_sidebar():
    st.sidebar.title("⚖️ Ovid.IA")
    st.sidebar.markdown("---")
    menu = st.sidebar.radio(
        "Navegação",
        [
            "Auditoria de Contratos", 
            "Busca de Jurisprudência", 
            "Resumo de Autos",
            "Redação e Estilometria",
            "Gestão de Prazos (Diário Oficial)"
        ],
        index=0
    )
    st.sidebar.markdown("---")
    st.sidebar.info(
        "**Sobre o Protótipo**\n\n"
        "Este é um ambiente de demonstração de alta fidelidade "
        "para ilustrar as capacidades de uma IA Jurídica."
    )
    return menu

def page_auditoria_contratos():
    st.markdown('<h1 class="title-text">Auditoria de Contratos (Análise de Risco)</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle-text">Foco em compliance e gestão de risco operacional, varrendo minutas para apontar armadilhas antes da assinatura.</p>', unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("Faça o upload do contrato (Ex: Contrato_Locacao_Shopping.pdf)", type=["pdf", "docx", "txt"])
    
    if uploaded_file is not None:
        with st.spinner("Analisando o documento em busca de riscos..."):
            time.sleep(2)
        
        st.success("Análise de Conformidade Concluída!")
        st.markdown("---")
        
        st.subheader("📊 Painel de Análise de Conformidade")
        
        col1, col2 = st.columns([1, 2])
        with col1:
            st.metric(label="Nível de Risco Geral", value="🔴 ALTO", delta="Requer Ação Imediata")
            st.metric(label="Alertas Encontrados", value="3")
            
        with col2:
            st.error("""
            **🚩 Alerta 1: Risco Extremo (Abusividade)**
            - **Local:** Cláusula Sexta - DO FORO.
            - **Descrição:** O contrato elege o foro da Comarca de Genebra, Suíça.
            - **Justificativa Legal:** Isso inviabiliza o acesso à justiça para as partes brasileiras e anula a cláusula. O CDC e o CPC preveem nulidade quando o foro dificulta a defesa.
            - **Recomendação:** Alterar para o foro do local do imóvel (São Paulo/SP).
            """)
            
            st.warning("""
            **🚩 Alerta 2: Risco Médio (Multa)**
            - **Local:** Cláusula Quarta - DA MULTA POR ATRASO.
            - **Descrição:** Multa moratória de 30% e juros de 2% ao dia.
            - **Justificativa Legal:** Multa de 30% é excessivamente onerosa e pode ser reduzida judicialmente por enriquecimento sem causa. Juros abusivos (Usura).
            - **Recomendação:** Limitar a multa a 10% (padrão de locação comercial) e juros de 1% ao mês.
            """)
            
            st.info("""
            **⚠️ Alerta 3: Atenção (Multa Rescisória)**
            - **Local:** Cláusula Quinta - DA RESCISÃO E BENFEITORIAS.
            - **Descrição:** Multa rescindenda de 10 aluguéis.
            - **Justificativa Legal:** Valor superior ao triplo da média de mercado (3 aluguéis). Risco de redução judicial da penalidade.
            - **Recomendação:** Ajustar para 3 aluguéis proporcionais.
            """)

def page_busca_jurisprudencia():
    st.markdown('<h1 class="title-text">Busca de Jurisprudência (RAG)</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle-text">Provas de explicabilidade e sem alucinações. Busca baseada em dados reais com citação de fontes.</p>', unsafe_allow_html=True)
    
    query = st.text_input("Pesquisar jurisprudência:", placeholder="Ex: Danos morais por overbooking em São Paulo, o dano é presumido (in re ipsa)?")
    
    if st.button("🔍 Pesquisar"):
        if query:
            with st.spinner("Analisando bases de jurisprudência (TJSP)..."):
                time.sleep(2)
                
            st.subheader("🔍 Resumo do Entendimento do TJSP (Com base nos últimos 24 meses)")
            st.write("Sim, o Tribunal de Justiça de São Paulo mantém o entendimento consolidado de que o overbooking gera dano moral presumido (in re ipsa), dispensando a prova do prejuízo sofrido pelo passageiro, desde que o atraso seja significativo ou gere transtornos extraordinários.")
            
            st.markdown("---")
            st.subheader("Decisões Relevantes Encontradas (Clique para abrir a fonte original):")
            
            with st.expander("📂 Recurso Inominado Cível 1000123-45.2026.8.26.0001 (TJSP)", expanded=True):
                st.markdown('"...Overbooking comprovado. Dano moral in re ipsa configurado. Quantum indenizatório mantido em R$ 8.000,00..."')
                st.info("**Fonte:** Página 3, parágrafo 2º, do acórdão publicado em 10/08/2026.")
                
            with st.expander("📂 Apelação Cível 1000567-89.2025.8.26.0100 (TJSP)", expanded=False):
                st.markdown('"...Tratando-se de transporte aéreo, o dano moral decorrente de overbooking é presumido, dispensando prova de dor ou sofrimento..."')
                st.info("**Fonte:** Ementa da decisão publicada em 15/05/2026.")
        else:
            st.warning("Por favor, insira um termo de busca.")

def page_resumo_autos():
    st.markdown('<h1 class="title-text">Resumo de Autos (Due Diligence / Intake)</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle-text">Transforma textos longos e não estruturados em um payload de dados organizados, pronto para ser consumido por um ERP.</p>', unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("Faça o upload do arquivo (Ex: Peticao_Inicial_Danos_Morais_Cliente123.pdf)", type=["pdf"])
    
    if uploaded_file is not None:
        with st.spinner("Processando e extraindo dados estruturados..."):
            time.sleep(2)
            
        st.success("Dados extraídos com sucesso!")
        st.markdown("---")
        
        dados_extraidos = {
            "Campo Extraído": ["Parte Autora", "Parte Ré", "Valor da Causa", "Natureza da Ação", "Fatos Principais", "Teses Principais", "Próximo Prazo Potencial"],
            "Valor Encontrado": [
                "João da Silva",
                "Companhia Aérea XPTO S/A",
                "R$ 35.000,00",
                "Ação de Indenização por Danos Morais e Materiais (Transporte Aéreo)",
                "Cliente alega que houve atraso de voo de 12 horas, causando perda de compromisso de trabalho e extravio temporário de bagagem.",
                "Dano moral in re ipsa por overbooking e responsabilidade objetiva do transportador.",
                "Contestação (Ré): Prazo de 15 dias úteis a contar da citação."
            ]
        }
        
        # Mostrando como tabela customizada e larga
        st.table(pd.DataFrame(dados_extraidos))

def page_redacao_estilometria():
    st.markdown('<h1 class="title-text">Redação e Estilometria (Geração de Esboço Customizado)</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle-text">Aprende o tom de voz do advogado ou do escritório, resolvendo o problema da "IA genérica".</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        fatos = st.text_area("Fatos do Caso (Insira em bullet points ou texto livre):", height=120, 
                             value="Cliente (Motorista A) estava parado no sinal vermelho na Rua das Flores quando foi atingido na traseira pelo Motorista B (AAA-1111) no dia 10/08. Não houve feridos, mas o porta-malas amassou. Testemunha Maria (contato).")
                             
        peca = st.text_input("Peça Desejada:", value="Contestação")
    
    with col2:
        tom_escrita = st.selectbox(
            "Estilo de Escrita / Tom",
            ["Dr. Sênior (Agressivo/Combativo)", "Padrão Escritório (Conservador)", "Objetivo/Direto (Legal Design)"]
        )
        st.write("")
        st.write("")
        btn_gerar = st.button("✍️ Gerar Esboço")

    if btn_gerar:
        with st.spinner(f"Gerando {peca} no estilo '{tom_escrita}'..."):
            time.sleep(2.5)
            
        st.success("Esboço gerado com sucesso!")
        st.markdown("---")
        
        texto_gerado = """
        **MERITÍSSIMO JUÍZO DA [Nº] VARA CÍVEL DA COMARCA DE SÃO PAULO/SP**

        **CONTESTAÇÃO**

        SOLUÇÕES EM TECNOLOGIA LTDA., já devidamente qualificada nos autos, por seu procurador infrafirmado, vem, mui respeitosamente, à presença de Vossa Excelência, apresentar CONTESTAÇÃO à absurda e inverídica Ação de Indenização movida pelo MOTORISTA B.

        **I. DOS FATOS:**
        A versão dos fatos narrada na petição inicial é fruto exclusivo da fértil imaginação do Requerente. A realidade, que será cabalmente provada, é diametralmente oposta.
        No dia 10/08, na Rua das Flores, o Requerido estava parado em absoluto compliance com a legislação de trânsito em virtude de sinalização semafórica vermelha.
        Sem qualquer cautela e de forma totalmente imprudente, o Requerente (Motorista B) não freou a tempo, colidindo violentamente contra a traseira do veículo parado do Requerido. Trata-se da aplicação inequívoca da presunção de culpa daquele que colide na traseira.

        **II. DO DIREITO:**
        É de sabença geral e jurisprudência pacífica que a culpa do motorista que colide na traseira de veículo parado é presumida. O Requerente falhou em seu dever de cuidado (art. 28 do CTB), devendo ser o único a arcar com os prejuízos de sua própria imprudência.

        [...]

        Diante do exposto, requer-se:
        a) A total IMPROCEDÊNCIA da ação.
        b) A condenação do Autor ao pagamento de custas e honorários.
        """
        
        st.info("Texto Pronto para Edição:")
        st.markdown(texto_gerado)

def page_gestao_prazos():
    st.markdown('<h1 class="title-text">Gestão de Prazos (Varridura de Diário Oficial)</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle-text">Monitoramento de riscos financeiros e de compliance, evitando a perda de prazos fatais.</p>', unsafe_allow_html=True)
    
    if st.button("📡 Varrer Diário Oficial (Hoje)"):
        with st.spinner("Acessando publicações diárias..."):
            time.sleep(2)
            
        st.subheader("📊 Painel de Triagem de Intimações - Data: 11/09/2026")
        st.markdown("**Processos Processados:** 150 (Em busca de \"Meus Clientes S.A.\")")
        st.markdown("**Novas Intimações Encontradas:** 3")
        st.markdown("---")
        
        st.markdown("### Novos Prazos Identificados:")
        
        dados_prazos = {
            "Processo nº": ["100123-45", "100567-89", "100999-11"],
            "Cliente": ["Meus Clientes Ltda.", "Cliente Fulano", "Soluções Tech"],
            "Tipo de Decisão (Mockado)": [
                "Despacho: Intimação para contestação (15 dias úteis).", 
                "Sentença: Publicação de sentença de parcial procedência. Prazo de apelação.", 
                "Despacho: Intimação para manifestação sobre prova pericial."
            ],
            "Prazo Detectado": ["Data Limite: 02/10/2026", "Data Limite: 25/09/2026", "Data Limite: 18/09/2026"],
            "Prioridade / Ação Necessária": [
                "🔴 ALTA (Distribuir para Equipe Cível)", 
                "🟡 MÉDIA (Análise de recurso sênior)", 
                "🟡 MÉDIA (Coletar informações técnicas)"
            ]
        }
        
        st.table(pd.DataFrame(dados_prazos))

def main():
    menu_selection = render_sidebar()
    
    if menu_selection == "Auditoria de Contratos":
        page_auditoria_contratos()
    elif menu_selection == "Busca de Jurisprudência":
        page_busca_jurisprudencia()
    elif menu_selection == "Resumo de Autos":
        page_resumo_autos()
    elif menu_selection == "Redação e Estilometria":
        page_redacao_estilometria()
    elif menu_selection == "Gestão de Prazos (Diário Oficial)":
        page_gestao_prazos()

if __name__ == "__main__":
    main()
