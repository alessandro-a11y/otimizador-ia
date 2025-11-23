from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import traceback
import openai

# Importações locais
from .models import Document
from .utils import extract_text

# MUDANÇA CRÍTICA: Importamos a função 'get_vectordb' em vez da variável 'vectordb'
# Isso evita que o Django tente carregar o banco de dados na inicialização (o que causava o erro).
from .rag import rag_query, get_vectordb
from langchain_core.documents import Document as LangchainDocument


def upload_pdf(request):
    """
    View para upload de currículos.
    Usa Lazy Loading para iniciar o banco de dados apenas quando necessário.
    """
    if request.method == "POST" and request.FILES.get("file"):
        try:
            uploaded_file = request.FILES["file"]
            title = request.POST.get("title", uploaded_file.name)

            # 1. Salva no Banco SQL (Django)
            doc_instance = Document.objects.create(
                title=title,
                file=uploaded_file
            )

            # 2. Extrai Texto (usando utils com OCR)
            file_path = doc_instance.file.path
            text_content = extract_text(file_path)

            # 3. Salva no Banco Vetorial (ChromaDB)
            if text_content and text_content.strip():
                # --- AQUI ESTÁ A CORREÇÃO ---
                # Chamamos a função para pegar o banco de dados agora.
                vectordb = get_vectordb()

                lc_doc = LangchainDocument(
                    page_content=text_content,
                    metadata={"source": file_path, "title": title}
                )
                vectordb.add_documents([lc_doc])

                # Atualiza o texto no SQL também
                doc_instance.text_content = text_content
                doc_instance.save()

                return render(request, 'optimizer/upload.html', {
                    "success": f"Currículo '{title}' processado com sucesso!"
                })
            else:
                return render(request, 'optimizer/upload.html', {
                    "error": "Não foi possível ler texto do arquivo. Se for imagem, verifique o OCR."
                })

        except Exception as e:
            print("ERRO NO UPLOAD:", e)
            traceback.print_exc()
            return render(request, 'optimizer/upload.html', {"error": f"Erro interno: {str(e)}"})

    return render(request, 'optimizer/upload.html')


@csrf_exempt
def ask_rag(request):
    """
    API de perguntas do Otimizador.
    """
    if request.method == "POST":
        import json
        try:
            body = json.loads(request.body.decode("utf-8"))
            q = body.get("q", "")

            if not q:
                return JsonResponse({"error": "Pergunta vazia"}, status=400)

            # Chama a função de RAG (que já trata o lazy loading internamente)
            resp = rag_query(q)
            return JsonResponse({"answer": resp})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Método inválido"}, status=405)