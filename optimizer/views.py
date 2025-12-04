import json
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render


@csrf_exempt
@require_http_methods(["GET", "POST"])
def process_uploaded_pdf_api(request):
    if request.method == 'POST':
        if 'file' in request.FILES:
            uploaded_file = request.FILES['file']
            
            try:
                
                extracted_text = f"✅ Texto extraído com sucesso do arquivo: {uploaded_file.name}. (Conteúdo de teste para a IA)"
                
                return JsonResponse({'extracted_text': extracted_text}, status=200)

            except Exception as e:
                return JsonResponse({'error': f"Erro interno de processamento de arquivo: {str(e)}"}, status=500)
        else:
            return JsonResponse({'error': 'Nenhum arquivo encontrado no POST.'}, status=400)
    
    return JsonResponse({'message': 'API de Otimizador de Currículo - OK'}, status=200)


@csrf_exempt
@require_http_methods(["POST"])
def ask_rag_api(request):
    try:
        data = json.loads(request.body)
        full_prompt = data.get('q')
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Requisição JSON inválida.'}, status=400)
    
    if not full_prompt:
        return JsonResponse({'error': 'Nenhum prompt fornecido.'}, status=400)

    
    ai_response = f"Resposta da IA para o prompt: '{full_prompt[:100]}...'"
    
    return JsonResponse({'answer': ai_response}, status=200)