from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import tempfile
import os

def generate_pdf(summary, kpis, question, answer, sources, sec_link=None):
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")

    # Register a Unicode-compatible TTF font (you can place 'DejaVuSans.ttf' in your project root)
    font_path = "dejavu-fonts-ttf-2.37/ttf/DejaVuSans.ttf" 
    pdfmetrics.registerFont(TTFont("DejaVu", font_path))

    c = canvas.Canvas(temp_file.name, pagesize=A4)
    width, height = A4
    text_obj = c.beginText(40, height - 50)
    text_obj.setFont("DejaVu", 12)

    def add_line(line, wrap_width=95):
        while len(line) > wrap_width:
            text_obj.textLine(line[:wrap_width])
            line = line[wrap_width:]
        text_obj.textLine(line)

    add_line("📊 AI Financial Report Summary")
    add_line("=" * 95)

    if sec_link:
        add_line(f"🔗 SEC Source: {sec_link}")
        add_line("")

    add_line("📋 Summary:")
    for line in summary.split("\n"):
        add_line(line)

    add_line("\n📌 Key Financial Metrics:")
    for key, value in kpis.items():
        add_line(f"• {key}: {value}")

    if question:
        add_line("\n💬 Q&A:")
        add_line(f"Q: {question}")
        add_line(f"A: {answer.strip()}")

        add_line("\n📚 Sources:")
        for i, doc in enumerate(sources):
            add_line(f"🔎 Source {i + 1}:")
            for line in doc.page_content.strip().split("\n"):
                add_line(line)

    c.drawText(text_obj)
    c.showPage()
    c.save()
    return temp_file.name
