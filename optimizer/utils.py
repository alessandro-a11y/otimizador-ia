import docx
import fitz  # PyMuPDF
import os
import pytesseract
from PIL import Image
from pdf2image import convert_from_path


def extract_text(file_path):
    """
    Extrai texto de PDF (texto ou imagem/scan), DOCX, TXT e imagens (JPG/PNG).
    Requer Tesseract OCR instalado no sistema.
    """
    ext = os.path.splitext(file_path)[1].lower()

    # 1. Processamento de PDF
    if ext == ".pdf":
        text = ""
        try:
            # Tenta extração rápida (se for PDF de texto selecionável)
            doc = fitz.open(file_path)
            for page in doc:
                text += page.get_text()

            # Se extraiu muito pouco texto (< 50 caracteres), assume que é SCAN/IMAGEM
            if len(text.strip()) < 50:
                print("⚠️ Texto insuficiente detectado no PDF. Acionando OCR (leitura de imagem)...")
                text = ""  # Limpa para garantir que não misture lixo

                try:
                    # Converte páginas do PDF em imagens
                    # Nota: Isso requer o 'poppler-utils' instalado no sistema Linux
                    images = convert_from_path(file_path)

                    for i, img in enumerate(images):
                        print(f"   Processando página {i + 1} com OCR...")
                        # Usa Tesseract para ler a imagem (lang='por' para português)
                        page_text = pytesseract.image_to_string(img, lang='por')
                        text += page_text + "\n"
                except Exception as ocr_error:
                    print(
                        f"❌ Erro no OCR do PDF: {ocr_error}. Verifique se poppler-utils e tesseract-ocr estão instalados.")

        except Exception as e:
            print(f"Erro ao ler PDF: {e}")

        return text

    # 2. Processamento de Word (.docx)
    elif ext == ".docx":
        try:
            d = docx.Document(file_path)
            return "\n".join([p.text for p in d.paragraphs])
        except Exception as e:
            return f"Erro ao ler DOCX: {str(e)}"

    # 3. Processamento de Arquivo de Texto (.txt)
    elif ext == ".txt":
        try:
            return open(file_path, "r", encoding="utf-8").read()
        except:
            # Fallback para codificação antiga (comum no Windows)
            return open(file_path, "r", encoding="latin-1").read()

    # 4. Processamento de Imagens Diretas (.jpg, .png, .bmp)
    elif ext in [".jpg", ".jpeg", ".png", ".bmp"]:
        try:
            print(f"Processando imagem {ext} com OCR...")
            return pytesseract.image_to_string(Image.open(file_path), lang='por')
        except Exception as e:
            return f"Erro ao ler imagem: {str(e)}"

    return ""