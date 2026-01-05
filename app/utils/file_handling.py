"""File handling utilities for document processing.

This module provides functions and classes for handling various file operations,
including file uploads, downloads, conversion between formats, and temporary
file management for the PowerCV application.
"""

import os
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

import PyPDF2
import pytesseract
from pdf2image import convert_from_path


def extract_text_from_docx(docx_path: str) -> str:
    """Extract text content from a DOCX file.

    Args:
        docx_path: Path to the DOCX file

    Returns:
        str: Extracted text content
    """
    try:
        from docx import Document
        doc = Document(docx_path)
        text = []
        for paragraph in doc.paragraphs:
            text.append(paragraph.text)
        return '\n'.join(text)
    except ImportError:
        return "Error: python-docx package is required for DOCX support. Install with: pip install python-docx"
    except Exception as e:
        return f"Error extracting text from DOCX: {str(e)}"


def extract_text_from_markdown(md_path: str) -> str:
    """Extract text content from a Markdown file.

    Args:
        md_path: Path to the Markdown file

    Returns:
        str: Extracted text content
    """
    try:
        with open(md_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        return f"Error reading Markdown file: {str(e)}"


def extract_text_from_txt(txt_path: str) -> str:
    """Extract text content from a TXT file.

    Args:
        txt_path: Path to the TXT file

    Returns:
        str: Extracted text content
    """
    try:
        with open(txt_path, 'r', encoding='utf-8') as file:
            return file.read()
    except UnicodeDecodeError:
        # Try with different encoding
        try:
            with open(txt_path, 'r', encoding='latin-1') as file:
                return file.read()
        except Exception as e:
            return f"Error reading TXT file: {str(e)}"
    except Exception as e:
        return f"Error reading TXT file: {str(e)}"


def extract_text_from_file(file_path: str, file_extension: str) -> str:
    """Extract text content from various file formats.

    Args:
        file_path: Path to the file
        file_extension: File extension (e.g., '.pdf', '.docx', '.md', '.txt')

    Returns:
        str: Extracted text content
    """
    file_extension = file_extension.lower()

    if file_extension == '.pdf':
        return extract_text_from_pdf(file_path)
    elif file_extension == '.docx':
        return extract_text_from_docx(file_path)
    elif file_extension in ['.md', '.markdown']:
        return extract_text_from_markdown(file_path)
    elif file_extension == '.txt':
        return extract_text_from_txt(file_path)
    else:
        return f"Unsupported file format: {file_extension}"


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text content from a PDF file.

    This function attempts to extract text in two ways:
    1. Direct text extraction using PyPDF2
    2. OCR using pytesseract if direct extraction doesn't yield enough text

    Args:
        pdf_path: Path to the PDF file

    Returns:
    -------
        str: Extracted text content
    """
    try:
        with open(pdf_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                text += page.extract_text() + "\n\n"

        # If we got a reasonable amount of text, return it
        if len(text.strip()) > 100:
            return text
    except Exception as e:
        print(f"Direct PDF text extraction failed: {e}")
        text = ""

    # If direct extraction failed or didn't get enough text, try OCR
    try:
        # Convert PDF to images
        images = convert_from_path(pdf_path)

        # Perform OCR on each image
        ocr_text = ""
        for i, image in enumerate(images):
            text = pytesseract.image_to_string(image)
            ocr_text += text + "\n\n"

        return ocr_text
    except Exception as e:
        print(f"OCR extraction failed: {e}")
        # If OCR fails but we have some text from direct extraction, use that
        if text:
            return text
        return f"Text extraction failed. Error: {str(e)}"


def save_pdf_file(content: bytes, filename: str, directory: str) -> str:
    """Save PDF content to a file in the specified directory.

    Args:
        content: PDF file content as bytes
        filename: Name for the saved file
        directory: Directory to save the file in

    Returns:
    -------
        str: Path to the saved file
    """
    # Ensure directory exists
    os.makedirs(directory, exist_ok=True)

    # Create file path
    file_path = os.path.join(directory, filename)

    # Write content to file
    with open(file_path, "wb") as file:
        file.write(content)

    return file_path
