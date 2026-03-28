import PyPDF2
import io

def extract_text_from_pdf(uploaded_file):
    """Extract text from uploaded PDF file."""
    text = ""
    try:
        # Read the uploaded file bytes
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.read()))
        
        for page_num, page in enumerate(pdf_reader.pages):
            page_text = page.extract_text()
            if page_text:
                text += f"\n--- Page {page_num + 1} ---\n"
                text += page_text
                
        return text.strip()
    
    except Exception as e:
        return f"Error reading PDF: {str(e)}"

def get_pdf_metadata(uploaded_file):
    """Get basic PDF info."""
    try:
        uploaded_file.seek(0)  # Reset file pointer
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.read()))
        return {
            "pages": len(pdf_reader.pages),
            "encrypted": pdf_reader.is_encrypted
        }
    except:
        return {"pages": "Unknown", "encrypted": False}