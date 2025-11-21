#!/usr/bin/env python3
"""
Convert Markdown to PDF using markdown and reportlab libraries.
"""

import markdown
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Preformatted
from reportlab.lib.colors import HexColor
from html.parser import HTMLParser
import re

class HTMLToParagraphs(HTMLParser):
    """Convert HTML to ReportLab flowables."""
    
    def __init__(self, styles):
        super().__init__()
        self.styles = styles
        self.flowables = []
        self.current_text = []
        self.current_style = 'BodyText'
        self.in_pre = False
        self.in_code = False
        self.list_level = 0
        
    def handle_starttag(self, tag, attrs):
        if tag == 'h1':
            self.current_style = 'Heading1'
        elif tag == 'h2':
            self.current_style = 'Heading2'
        elif tag == 'h3':
            self.current_style = 'Heading3'
        elif tag == 'h4':
            self.current_style = 'Heading4'
        elif tag == 'p':
            self.current_style = 'BodyText'
        elif tag == 'pre':
            self.in_pre = True
        elif tag == 'code':
            self.in_code = True
            if not self.in_pre:
                self.current_text.append('<font name="Courier" color="#666666" backColor="#f5f5f5">')
        elif tag == 'strong' or tag == 'b':
            self.current_text.append('<b>')
        elif tag == 'em' or tag == 'i':
            self.current_text.append('<i>')
        elif tag == 'li':
            self.current_text.append('• ')
        elif tag == 'br':
            self.current_text.append('<br/>')
            
    def handle_endtag(self, tag):
        if tag in ['h1', 'h2', 'h3', 'h4', 'p']:
            text = ''.join(self.current_text).strip()
            if text:
                self.flowables.append(Paragraph(text, self.styles[self.current_style]))
                self.flowables.append(Spacer(1, 0.1 * inch))
            self.current_text = []
            self.current_style = 'BodyText'
        elif tag == 'pre':
            text = ''.join(self.current_text).strip()
            if text:
                self.flowables.append(Preformatted(text, self.styles['Code']))
                self.flowables.append(Spacer(1, 0.2 * inch))
            self.current_text = []
            self.in_pre = False
        elif tag == 'code':
            if not self.in_pre:
                self.current_text.append('</font>')
            self.in_code = False
        elif tag in ['strong', 'b']:
            self.current_text.append('</b>')
        elif tag in ['em', 'i']:
            self.current_text.append('</i>')
        elif tag == 'li':
            text = ''.join(self.current_text).strip()
            if text:
                self.flowables.append(Paragraph(text, self.styles['BodyText']))
            self.current_text = []
            
    def handle_data(self, data):
        if data.strip():
            self.current_text.append(data)

def convert_md_to_pdf(md_file, pdf_file=None):
    """
    Convert a Markdown file to PDF using ReportLab.
    
    Args:
        md_file: Path to the markdown file
        pdf_file: Path to the output PDF file (optional, defaults to same name as md_file)
    """
    md_path = Path(md_file)
    
    if pdf_file is None:
        pdf_file = md_path.with_suffix('.pdf')
    else:
        pdf_file = Path(pdf_file)
    
    # Read the markdown file
    with open(md_path, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Convert markdown to HTML
    html_content = markdown.markdown(md_content, extensions=['extra', 'fenced_code', 'tables'])
    
    # Create PDF document
    doc = SimpleDocTemplate(
        str(pdf_file),
        pagesize=letter,
        leftMargin=1*inch,
        rightMargin=1*inch,
        topMargin=1*inch,
        bottomMargin=1*inch
    )
    
    # Get styles
    styles = getSampleStyleSheet()
    
    # Add custom code style if it doesn't exist
    if 'Code' not in styles:
        styles.add(ParagraphStyle(
            name='Code',
            parent=styles['Normal'],
            fontName='Courier',
            fontSize=9,
            leftIndent=20,
            rightIndent=20,
            backColor=HexColor('#f5f5f5'),
            borderColor=HexColor('#cccccc'),
            borderWidth=1,
            borderPadding=10,
            spaceAfter=10
        ))
    
    # Parse HTML and convert to flowables
    parser = HTMLToParagraphs(styles)
    parser.feed(html_content)
    
    # Build PDF
    doc.build(parser.flowables)
    
    print(f"✅ Successfully converted {md_path.name} to {pdf_file.name}")
    print(f"📄 PDF saved to: {pdf_file.absolute()}")
    
    return pdf_file

if __name__ == "__main__":
    # Convert the simple_user_guide.md to PDF
    convert_md_to_pdf("simple_user_guide.md")
