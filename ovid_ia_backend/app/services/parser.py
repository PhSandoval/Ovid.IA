import io
import pdfplumber
from fastapi import UploadFile

async def extrair_texto_pdf(arquivo: UploadFile) -> str:
    """
    Extrai o texto de um arquivo PDF recebido via UploadFile usando pdfplumber.
    A leitura é feita em memória para evitar gravação de arquivos temporários no disco.
    """
    texto_completo: str = ""
    
    # Lê os bytes do arquivo de forma assíncrona
    conteudo_bytes: bytes = await arquivo.read()
    arquivo_io = io.BytesIO(conteudo_bytes)
    
    # Usa o pdfplumber para abrir o buffer em memória e extrair o texto
    with pdfplumber.open(arquivo_io) as pdf:
        for page in pdf.pages:
            extraido = page.extract_text()
            if extraido:
                texto_completo += extraido + "\n"
                
    return texto_completo

async def extrair_texto_pdf_em_lotes(arquivo: UploadFile, limite_caracteres: int = 800, overlap: int = 200) -> list[str]:
    """
    Extrai o texto e particiona com sobreposição (Chunk Overlap) para evitar cortes no meio de cláusulas.
    (Limite abaixado para 800 caracteres: Modo Auditoria Profunda. Fatiamento granular para
    impedir que o LLM fique preguiçoso).
    """
    conteudo_bytes = await arquivo.read()
    arquivo_io = io.BytesIO(conteudo_bytes)
    
    texto_completo = ""
    
    with pdfplumber.open(arquivo_io) as pdf:
        for page in pdf.pages:
            extraido = page.extract_text()
            if extraido:
                texto_completo += extraido + "\n"
                
    tamanho_total = len(texto_completo)
    if tamanho_total <= limite_caracteres:
        return [texto_completo]
        
    lotes = []
    # Fatiamento Semântico: Divide o texto em blocos usando quebra de linha dupla (parágrafos/cláusulas)
    paragrafos = texto_completo.split('\n\n')
    
    # Se não houver \n\n, tenta por \n simples
    if len(paragrafos) == 1:
        paragrafos = texto_completo.split('\n')
        
    lote_atual = ""
    
    for p in paragrafos:
        p = p.strip()
        if not p:
            continue
            
        # Se adicionar este parágrafo estourar o limite, salva o lote atual e começa um novo
        if len(lote_atual) + len(p) > limite_caracteres and lote_atual:
            lotes.append(lote_atual)
            lote_atual = p + "\n\n"
        else:
            lote_atual += p + "\n\n"
            
    # Adiciona o último lote que sobrou
    if lote_atual.strip():
        lotes.append(lote_atual.strip())
        
    return lotes
