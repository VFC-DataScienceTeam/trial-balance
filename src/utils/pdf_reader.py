"""Utility to extract text and tables from PDF files."""

import pdfplumber
from pathlib import Path


def extract_text_from_pdf(pdf_path):
    """Extract all text from a PDF file.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        str: Extracted text from all pages
    """
    text_content = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, 1):
            text = page.extract_text()
            if text:
                text_content.append(f"--- Page {page_num} ---\n{text}\n")
    
    return "\n".join(text_content)


def extract_tables_from_pdf(pdf_path):
    """Extract tables from a PDF file.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        list: List of tuples (page_num, table_data)
    """
    tables = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, 1):
            page_tables = page.extract_tables()
            for table_idx, table in enumerate(page_tables):
                tables.append({
                    'page': page_num,
                    'table_index': table_idx,
                    'data': table
                })
    
    return tables


def get_pdf_info(pdf_path):
    """Get basic information about a PDF.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        dict: PDF metadata
    """
    with pdfplumber.open(pdf_path) as pdf:
        return {
            'num_pages': len(pdf.pages),
            'metadata': pdf.metadata,
            'page_dimensions': [(p.width, p.height) for p in pdf.pages]
        }


if __name__ == "__main__":
    # Example usage
    pdf_file = Path(__file__).parent.parent.parent / "docs" / "DGD - Trial Balance - v1.0.docx.pdf"
    
    if pdf_file.exists():
        print("PDF Information:")
        info = get_pdf_info(pdf_file)
        print(f"Pages: {info['num_pages']}")
        print(f"Metadata: {info['metadata']}")
        print("\n" + "="*80 + "\n")
        
        print("Extracting text...")
        text = extract_text_from_pdf(pdf_file)
        print(text)
        print("\n" + "="*80 + "\n")
        
        print("Extracting tables...")
        tables = extract_tables_from_pdf(pdf_file)
        print(f"Found {len(tables)} tables")
        for table_info in tables:
            print(f"\nPage {table_info['page']}, Table {table_info['table_index']}:")
            for row in table_info['data'][:5]:  # Show first 5 rows
                print(row)
    else:
        print(f"PDF file not found: {pdf_file}")
