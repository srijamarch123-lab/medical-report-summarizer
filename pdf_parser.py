import PyPDF2
import io
import pytesseract
from PIL import Image
import pdf2image
import os

# Point to Tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Point to Poppler
POPPLER_PATH = r'C:\poppler\Library\bin'

def extract_text_from_pdf(uploaded_file):
    """Try normal extraction first, fall back to OCR if needed."""
    
    # First try normal text extraction
    text = extract_text_normal(uploaded_file)
    
    if text and len(text.strip()) > 100:  # If we got decent text
        return text
    
    # If that fails, try OCR
    uploaded_file.seek(0)
    return extract_text_ocr(uploaded_file)


def extract_text_normal(uploaded_file):
    """Extract text from text-based PDFs."""
    text = ""
    try:
        uploaded_file.seek(0)
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.read()))
        for page_num, page in enumerate(pdf_reader.pages):
            page_text = page.extract_text()
            if page_text:
                text += f"\n--- Page {page_num + 1} ---\n"
                text += page_text
        return text.strip()
    except Exception as e:
        return ""


def extract_text_ocr(uploaded_file):
    """Extract text from scanned/image PDFs using OCR."""
    try:
        uploaded_file.seek(0)
        file_bytes = uploaded_file.read()
        
        # Convert PDF pages to images
        images = pdf2image.convert_from_bytes(
            file_bytes,
            poppler_path=POPPLER_PATH
        )
        
        text = ""
        for i, image in enumerate(images):
            text += f"\n--- Page {i + 1} ---\n"
            # Run OCR on each page image
            page_text = pytesseract.image_to_string(image)
            text += page_text
        
        return text.strip() if text.strip() else "Error: Could not extract text from this PDF."
    
    except Exception as e:
        return f"OCR Error: {str(e)}"


def get_pdf_metadata(uploaded_file):
    """Get basic PDF info."""
    try:
        uploaded_file.seek(0)
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.read()))
        return {
            "pages": len(pdf_reader.pages),
            "encrypted": pdf_reader.is_encrypted
        }
    except:
        return {"pages": "Unknown", "encrypted": False}