from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage
import traceback

# Importamos a função de extração local (do arquivo utils.py desta pasta)
from .utils import extract_text

# Importamos a inteligência específica do LinkedIn e o Lazy Loader do banco
from .rag import analyze_linkedin_profile, get_vectordb
from langchain_core.documents import Document as LangchainDocument


def linkedin_home(request):
    """
    Tela principal de análise do LinkedIn.
    Recebe o PDF, extrai o texto e salva na memória da IA.
    """
    if request.method == "POST" and request.FILES.get("file"):
        try:
            uploaded_file = request.FILES["file"]

            # 1. Salva o arquivo temporariamente
            fs = FileSystemStorage()
            filename = fs.save(f"linkedin_{uploaded_file.name}", uploaded_file)
            file_path = fs.path(filename)

            # 2. Extrai Texto (Usa a função local do utils.py deste app)
            text_content = extract_text(file_path)

            if text_content and text_content.strip():
                # 3. Inicia o Banco Vetorial (Lazy Load)
                vectordb = get_vectordb()

                # Limpa memória anterior para focar apenas neste perfil
                vectordb.delete_collection()

                # 4. Salva na memória da IA
                lc_doc = LangchainDocument(
                    page_content=text_content,
                    metadata={"source": file_path, "type": "linkedin"}
                )
                vectordb.add_documents([lc_doc])

                return render(request, 'linkedin_analyser/dashboard.html', {
                    "success": "Perfil carregado com sucesso! O especialista em LinkedIn está pronto."
                })
            else:
                return render(request, 'linkedin_analyser/dashboard.html', {
                    "error": "Não conseguimos ler o arquivo. Verifique se é um PDF válido."
                })

        except Exception as e:
            traceback.print_exc()
            return render(request, 'linkedin_analyser/dashboard.html', {
                "error": f"Erro interno: {str(e)}"
            })

    return render(request, 'linkedin_analyser/dashboard.html')


@csrf_exempt
def linkedin_ask(request):
    """
    API que recebe as perguntas sobre o perfil (via AJAX).
    """
    if request.method == "POST":
        import json
        try:
            body = json.loads(request.body.decode("utf-8"))
            question = body.get("q", None)

            if not question:
                return JsonResponse({"error": "Pergunta vazia"}, status=400)

            # Chama a IA especialista (definida no rag.py)
            answer = analyze_linkedin_profile(question)
            return JsonResponse({"answer": answer})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Método inválido"}, status=405)