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
