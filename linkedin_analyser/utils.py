import docx
import fitz  # PyMuPDF
import os
import pytesseract
from PIL import Image
from pdf2image import convert_from_path


def extract_text(file_path):
    """
    Versão local do extrator de texto para o Analisador de LinkedIn.
    Lê PDF (texto e imagem/scan), DOCX, TXT e Imagens.
    """
    ext = os.path.splitext(file_path)[1].lower()

    # 1. Processamento de PDF
    if ext == ".pdf":
        text = ""
        try:
            # Tenta ler como texto selecionável (rápido)
            doc = fitz.open(file_path)
            for page in doc:
                text += page.get_text()

            # Se extraiu pouco texto (< 50 chars), assume que é imagem/scan e usa OCR
            if len(text.strip()) < 50:
                try:
                    # Converte páginas em imagens para o Tesseract ler
                    images = convert_from_path(file_path)
                    for img in images:
                        text += pytesseract.image_to_string(img, lang='por') + "\n"
                except:
                    pass  # Ignora erro se não tiver OCR instalado
        except:
            pass
        return text

    # 2. Processamento de Word (.docx)
    elif ext == ".docx":
        try:
            d = docx.Document(file_path)
            return "\n".join([p.text for p in d.paragraphs])
        except:
            return ""

    # 3. Processamento de Arquivo de Texto (.txt)
    elif ext == ".txt":
        try:
            return open(file_path, "r", encoding="utf-8").read()
        except:
            return ""

    # 4. Processamento de Imagens Diretas (.jpg, .png, etc)
    elif ext in [".jpg", ".jpeg", ".png", ".bmp"]:
        try:
            return pytesseract.image_to_string(Image.open(file_path), lang='por')
        except:
            return ""

    return ""