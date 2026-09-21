from datetime import date, timedelta

def calcular_prazo_fatal(data_publicacao: date, dias_uteis: int) -> date:
    """
    Motor de Regras CPC Simplificado.
    A contagem inicia no primeiro dia útil subsequente à publicação e conta 
    apenas dias úteis (pulando sábados - 5, e domingos - 6).
    (MVP: ignora feriados).
    """
    # Se prazo é 0 (ex: ato imediato), o prazo fatal é a própria data (ou próximo dia útil).
    if dias_uteis == 0:
        return data_publicacao

    data_atual = data_publicacao
    
    # 1. Pula o dia do começo (Art. 224 do CPC: Exclui o dia do começo)
    data_atual += timedelta(days=1)
    
    # Se o primeiro dia da contagem for fds, empurra para segunda
    while data_atual.weekday() >= 5:
        data_atual += timedelta(days=1)

    dias_contados = 0
    # O primeiro dia já conta como dia 1 (depois de excluir o dia do começo e achar dia útil)
    dias_contados += 1
    
    # 2. Contar os próximos dias úteis
    while dias_contados < dias_uteis:
        data_atual += timedelta(days=1)
        if data_atual.weekday() < 5:  # Segunda a Sexta (0 a 4)
            dias_contados += 1
            
    return data_atual
