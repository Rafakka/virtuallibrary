import os
import ebooklib
from ebooklib import epub
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import re

class BookConverter:
    def __init__(self):
        pass
    
    def convert_epub_to_pdf(self, original_path):
        try:

            book = epub.read_epub(original_path)

            text_content = self._extract_epub_as_text(book)
            
            pdf_path = self.get_pdf_path(original_path)
            self._create_pdf_from_text(text_content, pdf_path)
            
            return pdf_path
            
        except Exception as e:
            raise Exception(f"EPUB conversion failed: {str(e)}")
    

    def _extract_epub_as_text(self, book):
        text_parts = []
        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                try:
                    content = item.get_content().decode('utf-8')
                    text = self._html_to_text(content)
                    text_parts.append(text)
                except Exception as e:
                    print(f"Warning: Could not process item: {e}")
                    continue
        return "\n".join(text_parts)
    
    def _html_to_text(self, html):
        """Simple HTML to text conversion using regex"""
        html = re.sub(r'<script.*?</script>', '', html, flags=re.DOTALL)
        html = re.sub(r'<style.*?</style>', '', html, flags=re.DOTALL)
        
        html = re.sub(r'<br\s*/?>', '\n', html)
        html = re.sub(r'<p.*?>', '\n', html)
        html = re.sub(r'<h[1-6].*?>', '\n', html)
        html = re.sub(r'<div.*?>', '\n', html)
        
        html = re.sub(r'<.*?>', '', html)
        
        html = html.replace('&nbsp;', ' ').replace('&amp;', '&')
        html = html.replace('&lt;', '<').replace('&gt;', '>')
        
        html = re.sub(r'\n\s*\n', '\n\n', html)
        return html.strip()
    
    def _create_pdf_from_text(self, text, pdf_path):
        doc = SimpleDocTemplate(pdf_path, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        normal_style = ParagraphStyle(
            'Normal',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=10,
            leading=14,
            spaceAfter=12,
        )
        
        paragraphs = text.split('\n\n')
        for para in paragraphs:
            if para.strip():
                clean_para = para.replace('\n', ' ').strip()
                if clean_para:
                    story.append(Paragraph(clean_para, normal_style))
                    story.append(Spacer(1, 6))
        
        doc.build(story)
    
    def get_pdf_path(self, original_path):
        base = os.path.splitext(original_path)[0]
        return base + '_converted.pdf'