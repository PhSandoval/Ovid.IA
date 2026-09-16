from fpdf import FPDF

pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", size=12)

texto = """
TRIBUNAL DE JUSTIÇA DO ESTADO DE SÃO PAULO
3ª Vara Cível da Comarca de São Paulo/SP

Processo nº: 1002345-67.2026.8.26.0100
Autor: Marcos Silva
Réu: Empresa de Telefonia S.A.

INTIMAÇÃO DE DESPACHO / DECISÃO

Ficam as partes intimadas do despacho/decisão abaixo proferido:

"Vistos.
Diante da juntada do laudo pericial (fls. 230-245), intimem-se as partes para que, querendo, apresentem suas manifestações e impugnações ao laudo, no prazo legal de 15 (quinze) dias úteis, sob pena de preclusão.
Após, com ou sem manifestação, tornem os autos conclusos para sentença.

São Paulo, 15 de Setembro de 2026.
João da Silva - Juiz de Direito"

PUBLICAÇÃO NO DIÁRIO OFICIAL ELETRÔNICO:
Data da disponibilização: 15/09/2026
"""

# Converter string para lidar com acentos em latin-1
pdf.multi_cell(0, 10, texto.encode('latin-1', 'replace').decode('latin-1'))
pdf.output("/Users/pedro/Documents/Ovid.IA/intimacao_teste.pdf")
print("Intimação de teste criada com sucesso!")
