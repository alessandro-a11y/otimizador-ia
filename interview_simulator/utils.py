import docx
import fitz  # PyMuPDF
import os
import pytesseract
from PIL import Image
from pdf2image import convert_from_path


def extract_text(file_path):
    """
    Versão local do extrator de texto para o Simulador de Entrevista.
    """
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        text = ""
        try:
            doc = fitz.open(file_path)
            for page in doc:
                text += page.get_text()

            # Se não extraiu texto (scan), tenta OCR
            if len(text.strip()) < 50:
                try:
                    images = convert_from_path(file_path)
                    for img in images:
                        text += pytesseract.image_to_string(img, lang='por') + "\n"
                except:
                    pass
        except:
            pass
        return text

    elif ext == ".docx":
        try:
            d = docx.Document(file_path)
            return "\n".join([p.text for p in d.paragraphs])
        except:
            return ""

    elif ext == ".txt":
        try:
            return open(file_path, "r", encoding="utf-8").read()
        except:
            return ""

    elif ext in [".jpg", ".jpeg", ".png", ".bmp"]:
        try:
            return pytesseract.image_to_string(Image.open(file_path), lang='por')
        except:
            return ""

    return ""