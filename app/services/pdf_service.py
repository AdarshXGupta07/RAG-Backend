import pdfplumber
import io

def extract_text_from_pdf(file_bytes: bytes):
    pdf_file = io.BytesIO(file_bytes)

    with pdfplumber.open(pdf_file) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text() or ""

    return text