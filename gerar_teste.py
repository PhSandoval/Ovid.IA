from fpdf import FPDF

class PDF(FPDF):
    def header(self):
        self.set_font('helvetica', 'B', 15)
        self.cell(0, 10, 'CONTRATO DE PRESTAÇÃO DE SERVIÇOS (MINUTA DE TESTE)', border=0, align='C', new_x="LMARGIN", new_y="NEXT")
        self.ln(10)

    def chapter_title(self, txt):
        self.set_font('helvetica', 'B', 12)
        self.cell(0, 10, txt, border=0, align='L', new_x="LMARGIN", new_y="NEXT")
        self.ln(4)

    def chapter_body(self, txt):
        self.set_font('helvetica', '', 11)
        self.multi_cell(0, 8, txt)
        self.ln(8)

pdf = PDF()
pdf.add_page()

# CLÁUSULA 1: Erros Ortográficos e Gramaticais
pdf.chapter_title('CLÁUSULA PRIMEIRA - Do Objeto (Erros Ortográficos)')
body1 = (
    "As parte concorda em asinar este contrato para a prestassão de servissos de contabilidade. "
    "O contratado deve realisar todas as tarefa com menas pressa e mais atençao. "
    "Nós vai enviar os relatórios para análise todo mês sem falta, e qualquer atrasu implicará nas penalidade."
)
pdf.chapter_body(body1)

# CLÁUSULA 2: Risco Jurídico (Multa Abusiva)
pdf.chapter_title('CLÁUSULA SEGUNDA - Das Penalidades e Multas (Risco Jurídico Extremo)')
body2 = (
    "Fica estipulado que em caso de atraso no pagamento de qualquer parcela por parte do CONTRATANTE, "
    "incidirá automaticamente uma multa punitiva irredutível de 45% (quarenta e cinco por cento) sobre o valor total do contrato, "
    "além de juros moratórios de 5% ao dia. A falta de pagamento por mais de 5 dias resultará na perda total dos bens dados em garantia."
)
pdf.chapter_body(body2)

# CLÁUSULA 3: Ambiguidade Textual
pdf.chapter_title('CLÁUSULA TERCEIRA - Dos Prazos (Ambiguidade)')
body3 = (
    "O serviço será concluído o mais rápido possível após o pagamento, ou quando a equipe técnica achar que já trabalhou o suficiente. "
    "Se o tempo estiver chuvoso, os prazos podem mudar um pouco dependendo da situação do fornecedor principal."
)
pdf.chapter_body(body3)

# CLÁUSULA 4: Risco Jurídico (Foro e Direitos)
pdf.chapter_title('CLÁUSULA QUARTA - Do Foro e Renúncia de Direitos')
body4 = (
    "Fica eleito o foro da cidade de Nova York, Estados Unidos, para dirimir quaisquer dúvidas decorrentes deste contrato, "
    "renunciando o CONTRATANTE a qualquer outro, por mais privilegiado que seja, bem como renuncia desde já "
    "ao direito de buscar defesa técnica por meio do Procon ou qualquer órgão de defesa do consumidor."
)
pdf.chapter_body(body4)

# CLÁUSULA 5: Mistura de Erros
pdf.chapter_title('CLÁUSULA QUINTA - Rescisão')
body5 = (
    "O contrato podera cer cancelado se a contratante quiser, mas se vcs cancelar, não tem direito a estorno. "
    "A rescisão imotivada está estritamente proibida a menos que seja aprovada pela diretoria em reunião secreta."
)
pdf.chapter_body(body5)

pdf.output('/Users/pedro/Documents/Ovid.IA/contrato_teste_erros.pdf')
print("PDF gerado com sucesso!")
