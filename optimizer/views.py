from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
import os

def upload_pdf(request):
    if request.method == 'POST' and request.FILES.get('pdf'):
        pdf = request.FILES['pdf']
        fs = FileSystemStorage()
        filename = fs.save(pdf.name, pdf)
        file_path = fs.path(filename)

        return render(request, 'upload_success.html', {"file_path": file_path})

    return render(request, 'upload.html')


def ask_rag(request):
    if request.method == 'POST':
        pergunta = request.POST.get('pergunta')

        # IA SIMPLES (placeholder)
        resposta = f"Resposta gerada pela IA para: {pergunta}"

        return JsonResponse({"resposta": resposta})

    return JsonResponse({"erro": "Método não permitido"}, status=405)
