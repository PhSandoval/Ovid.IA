import streamlit as st
import requests
import json
from export_utils import gerar_docx_parecer, gerar_docx_intake

st.set_page_config(layout="wide", page_title="Ovid.IA")

# --- Injeção de Gestão de Estado (Session State) ---
if "rag_resultado" not in st.session_state: st.session_state.rag_resultado = None
if "rag_pergunta" not in st.session_state: st.session_state.rag_pergunta = None
if "intake_resultado" not in st.session_state: st.session_state.intake_resultado = None
if "auditoria_resultado" not in st.session_state: st.session_state.auditoria_resultado = None

# URL Base# Configuração da API
API_URL = "http://127.0.0.1:8000"

st.sidebar.title("⚖️ Ovid.IA")
st.sidebar.markdown("---")
menu = st.sidebar.radio(
    "Módulos",
    [
        "Auditoria de Contratos",
        "Revisão Gramatical",
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
        # Cria os elementos visuais vazios que serão atualizados dinamicamente
        progress_text = st.empty()
        progress_bar = st.progress(0)
        resultado_container = st.container()

        try:
            import time
            st.session_state.inicio_processamento = time.time()
            
            files = {"arquivo": (arquivo_upload.name, arquivo_upload.getvalue(), "application/pdf")}
            # Habilita o streaming no requests
            with requests.post(f"{API_URL}/contratos/analisar", files=files, stream=True) as response:
                if response.status_code != 200:
                    st.error(f"Erro na API: {response.text}")
                else:
                    # Lê linha por linha conforme o backend envia (Streaming)
                    for line in response.iter_lines():
                        if line:
                            import json
                            data = json.loads(line)
                            
                            if data.get("status") == "processando":
                                lote = data["lote_atual"]
                                total = data["total_lotes"]
                                # O progresso REAL é o que já foi concluído (lote anterior)
                                lotes_concluidos = lote - 1
                                percentual = int((lotes_concluidos / total) * 100)
                                
                                # Calcula tempo estimado dinamicamente baseado na performance real da máquina
                                if lotes_concluidos > 0:
                                    tempo_passado = time.time() - st.session_state.inicio_processamento
                                    tempo_medio_por_lote = tempo_passado / lotes_concluidos
                                else:
                                    tempo_medio_por_lote = 55  # Palpite inicial pessimista para a primeira volta
                                    
                                tempo_restante = int((total - lotes_concluidos) * tempo_medio_por_lote)
                                minutos = tempo_restante // 60
                                segundos = tempo_restante % 60
                                
                                # Anima a UI
                                progress_text.info(f"⏳ Ovid.IA está lendo o trecho {lote} de {total}... ({percentual}%) | 🕒 Tempo restante: ~{minutos}m {segundos}s (Auditoria Profunda)")
                                progress_bar.progress(percentual)
                                
                            elif data.get("status") == "lote_concluido":
                                lote = data["lote_atual"]
                                total = data["total_lotes"]
                                # Agora sim esse lote foi concluído
                                lotes_concluidos = lote
                                percentual = int((lotes_concluidos / total) * 100)
                                
                                progress_text.info(f"✅ Lote {lote} analisado! ({percentual}%)")
                                progress_bar.progress(percentual)
                                
                            elif data.get("status") == "concluido":
                                progress_text.success("🎯 Análise Completa Finalizada!")
                                progress_bar.progress(100)
                                st.session_state.auditoria_resultado = data["resultado"]
                                
        except requests.exceptions.ConnectionError:
            st.error("Falha de conexão: O Backend (FastAPI) não está rodando. Por favor, inicie o servidor na porta 8000.")
        except Exception as e:
            st.error(f"Ocorreu um erro inesperado: {str(e)}")

    if st.session_state.auditoria_resultado:
        dados = st.session_state.auditoria_resultado
        if dados['total_alertas'] > 0:
            st.success(f"Foram encontrados {dados['total_alertas']} alerta(s).")
        else:
            st.success("Nenhum risco de compliance encontrado neste documento.")
            
        st.subheader(f"Nível de Risco Geral: {dados['nivel_risco_geral']}")
        
        for alerta in dados["alertas"]:
            nivel = alerta.get("nivel_risco", "BAIXO").upper()
            categoria = alerta.get("categoria", "RISCO JURÍDICO")
            
            titulo_alerta = f"[{categoria}] **{nivel}** | {alerta.get('clausula', 'Sem Cláusula')}"
            
            if "EXTREMO" in nivel or "CRÍTICO" in nivel:
                st.error(f"🚩 {titulo_alerta}")
            elif categoria == "ERRO ORTOGRÁFICO/GRAMATICAL":
                st.info(f"✍️ {titulo_alerta}")
            elif categoria == "AMBIGUIDADE TEXTUAL":
                st.warning(f"🤔 {titulo_alerta}")
            else:
                st.warning(f"⚠️ {titulo_alerta}")
                
            st.write(f"**Descrição:** {alerta.get('descricao_risco', '')}")
            st.write(f"**Recomendação:** {alerta.get('recomendacao', '')}")
            st.markdown("---")

elif menu == "Revisão Gramatical":
    st.header("✍️ Revisão Gramatical e Ortográfica")
    st.write("Faça o upload de uma minuta para o Ovid.IA caçar erros de português, digitação e concordância.")
    
    arquivo_upload = st.file_uploader("Arraste seu PDF aqui", type=["pdf"], key="gramatica")
    
    if st.button("Corrigir Gramática") and arquivo_upload:
        progress_text = st.empty()
        progress_bar = st.progress(0)
        resultado_container = st.container()

        try:
            import time
            st.session_state.inicio_processamento = time.time()
            
            files = {"arquivo": (arquivo_upload.name, arquivo_upload.getvalue(), "application/pdf")}
            with requests.post(f"{API_URL}/contratos/revisar_gramatica", files=files, stream=True) as response:
                if response.status_code != 200:
                    st.error(f"Erro na API: {response.text}")
                else:
                    for line in response.iter_lines():
                        if line:
                            import json
                            data = json.loads(line)
                            
                            if data.get("status") == "processando":
                                lote = data["lote_atual"]
                                total = data["total_lotes"]
                                lotes_concluidos = lote - 1
                                percentual = int((lotes_concluidos / total) * 100)
                                
                                if lotes_concluidos > 0:
                                    tempo_passado = time.time() - st.session_state.inicio_processamento
                                    tempo_medio_por_lote = tempo_passado / lotes_concluidos
                                else:
                                    tempo_medio_por_lote = 55
                                    
                                tempo_restante = int((total - lotes_concluidos) * tempo_medio_por_lote)
                                minutos = tempo_restante // 60
                                segundos = tempo_restante % 60
                                
                                progress_text.info(f"⏳ Ovid.IA está lendo o trecho {lote} de {total}... ({percentual}%) | 🕒 Tempo restante: ~{minutos}m {segundos}s (Leitura Densa)")
                                progress_bar.progress(percentual)
                                
                            elif data.get("status") == "lote_concluido":
                                lote = data["lote_atual"]
                                total = data["total_lotes"]
                                percentual = int((lote / total) * 100)
                                progress_text.info(f"✅ Lote {lote} analisado! ({percentual}%)")
                                progress_bar.progress(percentual)
                                
                            elif data.get("status") == "concluido":
                                progress_text.success("🎯 Revisão Completa Finalizada!")
                                progress_bar.progress(100)
                                
                                dados = data["resultado"]
                                
                                with resultado_container:
                                    if dados['total_alertas'] > 0:
                                        st.success(f"Foram encontrados {dados['total_alertas']} erro(s) ortográfico(s).")
                                    else:
                                        st.success("Nenhum erro ortográfico ou de concordância encontrado!")
                                        
                                    for alerta in dados["alertas"]:
                                        titulo_alerta = f"[ERRO ORTOGRÁFICO] **BAIXO** | {alerta.get('clausula', 'Sem Cláusula')}"
                                        st.info(f"✍️ {titulo_alerta}")
                                        st.write(f"**O que está errado:** {alerta.get('descricao_risco', '')}")
                                        st.write(f"**Como corrigir:** {alerta.get('recomendacao', '')}")
                                        st.markdown("---")
        except requests.exceptions.ConnectionError:
            st.error("Falha de conexão: O Backend (FastAPI) não está rodando. Por favor, inicie o servidor na porta 8000.")

elif menu == "Busca de Jurisprudência":
    st.header("📚 Busca Semântica de Jurisprudência (RAG)")
    st.write("Crie seu acervo pessoal de jurisprudências e faça buscas inteligentes baseadas no sentido (e não apenas em palavras-chave).")
    
    aba_buscar, aba_indexar = st.tabs(["🔍 Buscar Tese", "📥 Alimentar Acervo"])
    
    with aba_indexar:
        st.subheader("Adicionar nova Jurisprudência")
        texto_ementa = st.text_area("Cole aqui o texto da Ementa ou Acórdão:", height=200)
        tribunal = st.text_input("Tribunal (Ex: TJSP, STJ, TST):")
        
        if st.button("Indexar no Banco Vetorial"):
            if texto_ementa and tribunal:
                with st.spinner("Vetorizando o texto no ChromaDB..."):
                    payload = {
                        "texto": texto_ementa,
                        "metadados": {"tribunal": tribunal}
                    }
                    resp = requests.post(f"{API_URL}/jurisprudencia/indexar", json=payload)
                    if resp.status_code == 200:
                        st.success("✅ Ementa salva e vetorizada com sucesso!")
                    else:
                        st.error("Falha ao salvar no banco.")
            else:
                st.warning("Preencha o texto e o tribunal.")
                
    with aba_buscar:
        st.subheader("Consultar o Acervo")
        query_busca = st.text_input("Qual é a sua tese jurídica ou dúvida?")
        
        fonte_busca = st.radio("Selecione a base de dados:", ["🔒 Acervo Local (ChromaDB)", "☁️ API Externa (Escavador)"])
        
        if st.button("Pesquisar com IA"):
            if query_busca:
                with st.spinner("O Ovid.IA está pesquisando as ementas e redigindo a resposta..."):
                    payload = {"query": query_busca}
                    
                    if "Externa" in fonte_busca:
                        endpoint = f"{API_URL}/jurisprudencia/buscar_externo"
                        resp = requests.post(endpoint, json=payload)
                        if resp.status_code == 200:
                            resultado = resp.json()
                            st.markdown("### 🤖 Parecer da IA")
                            st.info(resultado.get("resposta_ia", "Sem resposta."))
                            
                            st.markdown("### 📄 Precedentes Utilizados (Escavador)")
                            for i, fonte in enumerate(resultado.get("fontes", [])):
                                titulo = fonte.get('metadados', {}).get('titulo', 'Link')
                                link = fonte.get('metadados', {}).get('link', '#')
                                st.write(f"**Fonte {i+1} - [{titulo}]({link})**")
                                st.write(f"> {fonte.get('texto_recuperado', '')}")
                                st.markdown("---")
                        else:
                            st.error(f"Erro na busca: {resp.text}")
                    else:
                        # RAG LOCAL COM STREAMING
                        endpoint = f"{API_URL}/jurisprudencia/buscar"
                        
                        st.markdown("### 🤖 Parecer da IA")
                        parecer_placeholder = st.empty()
                        texto_acumulado = ""
                        fontes_recuperadas = []
                        
                        try:
                            with requests.post(endpoint, json=payload, stream=True) as resp:
                                if resp.status_code != 200:
                                    st.error(f"Erro na busca: {resp.text}")
                                else:
                                    import json
                                    for line in resp.iter_lines():
                                        if line:
                                            data = json.loads(line)
                                            status = data.get("status")
                                            
                                            if status == "no_results":
                                                parecer_placeholder.info("Nenhum precedente encontrado na base de dados para esta busca.")
                                            elif status == "fontes":
                                                fontes_recuperadas = data.get("fontes", [])
                                            elif status == "token":
                                                texto_acumulado += data.get("token", "")
                                                parecer_placeholder.info(texto_acumulado + "▌")
                                            elif status == "erro":
                                                st.error(data.get("erro"))
                                                
                                    # Tira o cursor piscante no final
                                    if texto_acumulado:
                                        parecer_placeholder.info(texto_acumulado)
                                        # SALVANDO NA SESSÃO
                                        st.session_state.rag_resultado = {
                                            "texto_acumulado": texto_acumulado,
                                            "fontes": fontes_recuperadas
                                        }
                                        st.session_state.rag_pergunta = query_busca

                        except Exception as e:
                            st.error(f"Erro ao conectar com a API de Streaming: {e}")

        # Renderiza a partir da Sessão (se houver histórico)
        if st.session_state.rag_resultado:
            # Mostra o Parecer novamente
            st.markdown("### 🤖 Parecer da IA")
            st.info(st.session_state.rag_resultado["texto_acumulado"])
            
            # Botão DOCX
            docx_buffer = gerar_docx_parecer(st.session_state.rag_pergunta, st.session_state.rag_resultado["texto_acumulado"])
            st.download_button(
                label="📄 Exportar Parecer para Word (.docx)",
                data=docx_buffer,
                file_name="parecer_rag_ovid_ia.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                type="primary"
            )
            
            # Renderiza as fontes
            if st.session_state.rag_resultado["fontes"]:
                st.markdown("### 📄 Precedentes Utilizados (Acervo Interno)")
                st.caption("ℹ️ **O que é o Score L2?** É a 'Distância Euclidiana' entre a sua pergunta e o processo no banco de dados. Quanto **menor** for esse número, mais a jurisprudência está 'colada' (semanticamente idêntica) ao que você perguntou.")
                for i, fonte in enumerate(st.session_state.rag_resultado["fontes"]):
                    trib = fonte.get('metadados', {}).get('tribunal', 'N/A')
                    st.write(f"**Fonte {i+1} ({trib}) - Score L2: {fonte.get('score', 0):.4f}**")
                    st.write(f"> {fonte.get('texto_recuperado', '')}")
                    st.markdown("---")


elif menu == "Resumo de Autos":
    st.header("📑 Intake: Resumo de Autos Processuais")
    st.write("Faça o upload de uma Petição Inicial extensa e deixe o Ovid.IA extrair as informações cruciais (Autor, Réu, Fatos e Pedidos) para a sua Ficha de Intake.")
    
    arquivo_autos = st.file_uploader("Arraste a Petição Inicial (PDF)", type=["pdf"], key="autos_upload")
    
    if arquivo_autos and st.button("Gerar Ficha de Intake"):
        with st.spinner("O Ovid.IA está analisando a petição e estruturando a Ficha de Intake..."):
            files = {"arquivo": (arquivo_autos.name, arquivo_autos.getvalue(), "application/pdf")}
            resp = requests.post(f"{API_URL}/autos/resumir", files=files)
            
            if resp.status_code == 200:
                st.session_state.intake_resultado = resp.json()
            else:
                st.error(f"Erro ao processar PDF: {resp.text}")

    # Renderiza apenas se houver resultado na sessão
    if st.session_state.intake_resultado:
        dados = st.session_state.intake_resultado
        st.success("Ficha de Intake gerada com sucesso!")
        
        # Renderizando o Painel de Intake de forma elegante
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 🧑‍⚖️ Partes")
            st.write(f"**Parte Autora:** {dados.get('parte_autora', 'N/A')}")
            st.write(f"**Parte Ré:** {dados.get('parte_re', 'N/A')}")
            
        with col2:
            st.markdown("### 🏷️ Natureza da Ação")
            st.write(f"**Ação:** {dados.get('natureza_acao', 'N/A')}")
            st.metric(label="Valor da Causa", value=str(dados.get('valor_causa', 'N/A')))
        
        st.markdown("---")
        
        # Fatos e Pedidos em caixas expansíveis (Acordeões) para não poluir a tela
        st.markdown("### 📝 Síntese dos Fatos")
        st.info(dados.get('sintese_fatos', 'N/A'))
        
        st.markdown("### 🎯 Pedidos Principais")
        for pedido in dados.get('pedidos_principais', []):
            st.markdown(f"- {pedido}")
            
        col_extra1, col_extra2 = st.columns(2)
        with col_extra1:
            with st.expander("Provas Listadas"):
                for prova in dados.get('provas_listadas', []):
                    st.write(f"- {prova}")
        with col_extra2:
            with st.expander("Tutela Antecipada (Liminar)"):
                st.write(dados.get('tutela_antecipada', 'N/A'))
                
        # Botão de Exportação para Word (.DOCX)
        st.markdown("---")
        docx_buffer = gerar_docx_intake(dados)
        st.download_button(
            label="📄 Exportar para Microsoft Word (.docx)",
            data=docx_buffer,
            file_name="ficha_intake_ovid_ia.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            type="primary"
        )

elif menu == "Gestão de Prazos":
    st.header("📅 Extração de Prazos Processuais")
    st.write("Faça o upload de uma intimação judicial (PDF) para extrair metadados para a sua agenda.")
    
    arquivo_upload = st.file_uploader("Arraste a Intimação/Publicação (PDF)", type=["pdf"], key="prazos")
    
    if st.button("Extrair Prazos") and arquivo_upload:
        with st.spinner("⏳ Lendo a intimação e calculando regras do CPC..."):
            try:
                files = {"arquivo": (arquivo_upload.name, arquivo_upload.getvalue(), "application/pdf")}
                response = requests.post(f"{API_URL}/prazos/extrair", files=files)
                
                if response.status_code == 200:
                    dados = response.json()
                    alertas = dados.get("resultados", [])
                    
                    st.success(f"🎯 Extração Concluída em {dados.get('tempo_processamento', 0):.1f} segundos!")
                    
                    if not alertas:
                        st.info("Nenhum prazo claro foi encontrado neste documento.")
                        
                    for alerta in alertas:
                        criticidade = (alerta.get('criticidade') or 'MEDIA').upper()
                        
                        if criticidade == "ALTA":
                            cor = "🔴"
                        elif criticidade == "MEDIA":
                            cor = "🟡"
                        else:
                            cor = "🟢"
                            
                        st.subheader(f"{cor} {alerta.get('tipo_ato_judicial', 'Ato Indefinido')}")
                        st.write(f"**Número do Processo:** {alerta.get('numero_processo', 'Não encontrado')}")
                        st.write(f"**Dias de Prazo:** {alerta.get('dias_prazo', 'N/A')} dias úteis")
                        st.write(f"**Data Fatal Estimada:** {alerta.get('data_fatal', 'Não calculado')}")
                        st.markdown("---")
                else:
                    st.error(f"Erro na API: {response.text}")
            except requests.exceptions.ConnectionError:
                st.error("Falha de conexão com o Backend.")
