import pdfplumber
import io

def extract_text_from_pdf(file_bytes: bytes):
    pdf_file = io.BytesIO(file_bytes)

    with pdfplumber.open(pdf_file) as pdf:
        text = ""
        for page in pdf.pages:
            page_text = page.dedupe_chars(tolerance=1).extract_text() or ""
            text += page_text

    return text