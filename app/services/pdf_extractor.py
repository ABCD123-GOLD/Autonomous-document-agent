import PyPDF2
from io import BytesIO
from typing import List, Dict

class PDFExtractor:
    @staticmethod
    def extract_text(file_content: bytes) -> List[Dict[str, str]]:
        """
        Extracts text from PDF bytes and returns a list of dictionaries 
        containing page number and text content.
        """
        pages = []
        try:
            reader = PyPDF2.PdfReader(BytesIO(file_content))
            for i, page in enumerate(reader.pages):
                text = page.extract_text()
                if text.strip():
                    pages.append({
                        "page_number": str(i + 1),
                        "text": text.strip()
                    })
        except Exception as e:
            # In a real production app, we would log this properly
            raise ValueError(f"Failed to extract text from PDF: {str(e)}")
            
        return pages

pdf_extractor = PDFExtractor()
