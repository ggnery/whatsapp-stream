from pathlib import Path
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

# Diretórios
TRANSCRIPTIONS_DIR = "transcriptions"
PDF_OUTPUT_DIR = "documents"


def setup_fonts():
    """
    Configura fontes para suportar caracteres especiais.
    Usa fontes do sistema ou fallback para fontes padrão.
    """
    try:
        # Tenta registrar fontes do sistema (Windows)
        if os.name == 'nt':  # Windows
            font_paths = [
                ("Arial", "C:\\Windows\\Fonts\\arial.ttf"),
                ("Arial-Bold", "C:\\Windows\\Fonts\\arialbd.ttf"),
            ]
            for font_name, font_path in font_paths:
                if os.path.exists(font_path):
                    pdfmetrics.registerFont(TTFont(font_name, font_path))
            return "Arial", "Arial-Bold"
    except Exception as e:
        print(f"[PDFGenerator] Aviso: Não foi possível carregar fontes personalizadas: {e}")
    
    # Fallback para fontes padrão
    return "Helvetica", "Helvetica-Bold"


def processar_markdown_para_pdf(md_path: Path, pdf_path: Path):
    """
    Converte um arquivo Markdown para PDF.
    
    Args:
        md_path: Caminho do arquivo .md
        pdf_path: Caminho de saída do .pdf
    """
    try:
        # Lê o conteúdo do markdown
        with open(md_path, "r", encoding="utf-8") as f:
            conteudo = f.read()
        
        # Configura o PDF
        doc = SimpleDocTemplate(
            str(pdf_path),
            pagesize=A4,
            rightMargin=inch*0.75,
            leftMargin=inch*0.75,
            topMargin=inch,
            bottomMargin=inch*0.75,
        )
        
        # Configura estilos
        font_normal, font_bold = setup_fonts()
        styles = getSampleStyleSheet()
        
        # Estilos personalizados
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor='#2C3E50',
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName=font_bold
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor='#34495E',
            spaceAfter=10,
            spaceBefore=12,
            fontName=font_bold
        )
        
        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['BodyText'],
            fontSize=10,
            alignment=TA_JUSTIFY,
            spaceAfter=6,
            fontName=font_normal
        )
        
        bullet_style = ParagraphStyle(
            'CustomBullet',
            parent=styles['BodyText'],
            fontSize=10,
            leftIndent=20,
            spaceAfter=4,
            fontName=font_normal
        )
        
        # Processa o conteúdo
        story = []
        lines = conteudo.split('\n')
        
        for line in lines:
            line = line.strip()
            
            if not line:
                story.append(Spacer(1, 0.1*inch))
                continue
            
            # Títulos principais (# Título)
            if line.startswith('# '):
                text = line[2:].strip()
                story.append(Paragraph(text, title_style))
                story.append(Spacer(1, 0.2*inch))
            
            # Subtítulos (## Subtítulo)
            elif line.startswith('## '):
                text = line[3:].strip()
                story.append(Paragraph(text, heading_style))
                story.append(Spacer(1, 0.1*inch))
            
            # Listas com bullets (- item ou * item)
            elif line.startswith('- ') or line.startswith('* '):
                text = '• ' + line[2:].strip()
                # Escapa caracteres especiais do XML
                text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                story.append(Paragraph(text, bullet_style))
            
            # Texto normal
            else:
                # Escapa caracteres especiais primeiro
                text = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                
                # Processa negrito markdown (**texto**) de forma correta
                # Divide por ** e alterna entre normal e negrito
                parts = text.split('**')
                if len(parts) > 1:
                    formatted = []
                    for i, part in enumerate(parts):
                        if i % 2 == 1:  # Partes ímpares estão dentro de **
                            formatted.append(f'<b>{part}</b>')
                        else:
                            formatted.append(part)
                    text = ''.join(formatted)
                
                story.append(Paragraph(text, body_style))
        
        # Gera o PDF
        try:
            doc.build(story)
        except Exception as build_error:
            print(f"[PDFGenerator] Erro ao construir PDF para {md_path.name}: {build_error}")
            return False
        
        # Verifica se o PDF foi criado com sucesso
        if pdf_path.exists() and pdf_path.stat().st_size > 0:
            return True
        else:
            print(f"[PDFGenerator] PDF não foi criado ou está vazio para {md_path.name}")
            return False
        
    except Exception as e:
        print(f"[PDFGenerator] Erro geral ao processar {md_path.name}: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """
    Processa todos os arquivos .md em transcriptions/ e gera PDFs correspondentes.
    Pula arquivos que já possuem PDF gerado.
    """
    print("\n" + "="*60)
    print("[PDFGenerator] Iniciando geração de PDFs")
    print("="*60)
    
    trans_dir = Path(TRANSCRIPTIONS_DIR)
    pdf_dir = Path(PDF_OUTPUT_DIR)
    
    # Verifica se o diretório de transcrições existe
    if not trans_dir.exists():
        print(f"[PDFGenerator] Erro: Diretório '{TRANSCRIPTIONS_DIR}' não encontrado.")
        return
    
    # Cria diretório de PDFs se não existir
    pdf_dir.mkdir(parents=True, exist_ok=True)
    
    # Encontra todos os arquivos .md
    md_files = list(trans_dir.glob("*.md"))
    
    if not md_files:
        print(f"[PDFGenerator] Nenhum arquivo .md encontrado em '{TRANSCRIPTIONS_DIR}'.")
        print(f"[PDFGenerator] Processamento concluído!")
        print(f"   PDFs gerados: 0")
        print(f"   Pulados (já existiam): 0")
        print(f"   Falhas: 0")
        return
    
    print(f"[PDFGenerator] {len(md_files)} arquivo(s) .md encontrado(s).")
    
    success_count = 0
    skip_count = 0
    fail_count = 0
    
    for md_file in md_files:
        pdf_filename = md_file.stem + ".pdf"
        pdf_path = pdf_dir / pdf_filename
        
        # Verifica se o PDF já existe
        if pdf_path.exists():
            skip_count += 1
            continue
        
        if processar_markdown_para_pdf(md_file, pdf_path):
            print(f"✅ PDF gerado: {pdf_filename}")
            success_count += 1
        else:
            fail_count += 1
    
    print("\n" + "="*60)
    print(f"[PDFGenerator] Processamento concluído!")
    print(f"   PDFs gerados: {success_count}")
    print(f"   Pulados (já existiam): {skip_count}")
    print(f"   Falhas: {fail_count}")
    print(f"   PDFs salvos em: {pdf_dir.resolve()}")
    print("="*60)


if __name__ == "__main__":
    main()