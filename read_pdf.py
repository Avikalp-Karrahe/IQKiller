#!/usr/bin/env python3
"""
PDF Reader Script
Extracts text content from PDF files using multiple methods.
"""

import PyPDF2
import pdfplumber
from pathlib import Path


def read_pdf_with_pypdf2(pdf_path: str) -> str:
    """Read PDF using PyPDF2."""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += f"\n--- Page {page_num + 1} ---\n"
                text += page.extract_text()
            return text
    except Exception as e:
        return f"PyPDF2 Error: {e}"


def read_pdf_with_pdfplumber(pdf_path: str) -> str:
    """Read PDF using pdfplumber."""
    try:
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                text += f"\n--- Page {page_num + 1} ---\n"
                page_text = page.extract_text()
                if page_text:
                    text += page_text
                else:
                    text += "[No text found on this page]"
        return text
    except Exception as e:
        return f"pdfplumber Error: {e}"


def main():
    """Main function to read the PDF."""
    pdf_path = "JRD_v1.1.pdf"
    
    if not Path(pdf_path).exists():
        print(f"Error: PDF file '{pdf_path}' not found!")
        return
    
    print("=" * 60)
    print("PDF CONTENT EXTRACTION")
    print("=" * 60)
    print(f"File: {pdf_path}")
    print()
    
    # Try PyPDF2 first
    print("📄 Using PyPDF2:")
    print("-" * 30)
    pypdf2_text = read_pdf_with_pypdf2(pdf_path)
    print(pypdf2_text[:1000])  # Show first 1000 characters
    if len(pypdf2_text) > 1000:
        print("... (truncated)")
    print()
    
    # Try pdfplumber as backup
    print("📄 Using pdfplumber:")
    print("-" * 30)
    pdfplumber_text = read_pdf_with_pdfplumber(pdf_path)
    print(pdfplumber_text[:1000])  # Show first 1000 characters
    if len(pdfplumber_text) > 1000:
        print("... (truncated)")
    print()
    
    # Save full content to file
    output_file = "pdf_content.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=== PyPDF2 EXTRACTION ===\n")
        f.write(pypdf2_text)
        f.write("\n\n=== PDFPLUMBER EXTRACTION ===\n")
        f.write(pdfplumber_text)
    
    print(f"✅ Full content saved to: {output_file}")
    print("=" * 60)


if __name__ == "__main__":
    main() 