import streamlit as st
import requests

st.set_page_config(layout="wide", page_title="Ovid.IA")

# URL Base do Backend Local
API_URL = "http://localhost:8000"

st.sidebar.title("⚖️ Ovid.IA")
st.sidebar.markdown("---")
menu = st.sidebar.radio(
    "Módulos",
    [
        "Auditoria de Contratos",
        "Busca de Jurisprudência",
        "Resumo de Autos",
        "Gestão de Prazos"
    ]
)

if menu == "Auditoria de Contratos":
    st.header("📄 Auditoria de Contratos (Classificador de Risco)")
    st.write("Faça o upload de uma minuta ou contrato em PDF para análise de conformidade.")
    
    arquivo_upload = st.file_uploader("Arraste seu PDF aqui", type=["pdf"])
    
    if st.button("Analisar Conformidade") and arquivo_upload:
        with st.spinner("Analisando cláusulas com IA Local..."):
            try:
                # Enviar o arquivo via POST form-data
                files = {"arquivo": (arquivo_upload.name, arquivo_upload.getvalue(), "application/pdf")}
                response = requests.post(f"{API_URL}/contratos/analisar", files=files)
                
                if response.status_code == 200:
                    dados = response.json()
                    
                    st.success(f"Análise concluída! Foram encontrados {dados['total_alertas']} alerta(s).")
                    st.subheader(f"Nível de Risco Geral: {dados['nivel_risco_geral']}")
                    
                    for alerta in dados["alertas"]:
                        nivel = alerta["nivel_risco"].upper()
                        # Renderizar cores dependendo da criticidade
                        if "EXTREMO" in nivel or "CRÍTICO" in nivel:
                            st.error(f"🚩 **{nivel}** | {alerta['clausula']}")
                        else:
                            st.warning(f"⚠️ **{nivel}** | {alerta['clausula']}")
                            
                        st.write(f"**Descrição:** {alerta['descricao_risco']}")
                        st.write(f"**Recomendação:** {alerta['recomendacao']}")
                        st.markdown("---")
                else:
                    st.error(f"Erro na API: {response.text}")
            except requests.exceptions.ConnectionError:
                st.error("Falha de conexão: O Backend (FastAPI) não está rodando. Por favor, inicie o servidor na porta 8000.")
            except Exception as e:
                st.error(f"Ocorreu um erro: {str(e)}")

elif menu == "Busca de Jurisprudência":
    st.header("📚 Busca Semântica de Jurisprudência (RAG)")
    st.info("Módulo em desenvolvimento. O backend já suporta indexação e busca!")

elif menu == "Resumo de Autos":
    st.header("📑 Intake: Resumo de Autos Processuais")
    st.info("Módulo em desenvolvimento. O endpoint /autos/resumir já está ativo no backend!")

elif menu == "Gestão de Prazos":
    st.header("📅 Gestão de Prazos e Diário Oficial")
    st.info("Módulo em desenvolvimento. O motor de cálculo do CPC já foi integrado!")
