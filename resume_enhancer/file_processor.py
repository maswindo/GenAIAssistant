import io
from docx import Document
import pdfplumber
import pytesseract

class FileProcessor:
    @staticmethod
    def extract_text(file_data):
        """
        Detects file type and extracts text accordingly.
        """
        try:
            file_like = io.BytesIO(file_data)
            if file_data[:4] == b'\x50\x4b\x03\x04':  # DOCX magic number
                return FileProcessor.extract_text_from_docx(file_like)
            else:
                return FileProcessor.extract_text_from_pdf(file_like)
        except Exception as e:
            return f"Error extracting text: {e}"

    @staticmethod
    def extract_text_from_docx(file_like):
        """
        Extract text from DOCX files.
        """
        try:
            document = Document(file_like)
            return "\n".join([para.text for para in document.paragraphs])
        except Exception as e:
            return f"Error extracting DOCX text: {e}"

    @staticmethod
    def extract_text_from_pdf(file_like):
        """
        Extract text from PDF files.
        """
        with pdfplumber.open(file_like) as pdf:
            resume_text = ""
            for page in pdf.pages:
                page_text = page.extract_text()
                resume_text += page_text if page_text else ""
            return resume_text
