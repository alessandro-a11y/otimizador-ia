import requests
import json
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt

# URL da API externa que processa os dados.
EXTERNAL_API_URL = "https://otimizador-ia-5mkw.onrender.com"

# ==============================================================================
# VIEW PARA O UPLOAD DO CURRÍCULO
# Rota: /upload/ (name='upload_route')
# ==============================================================================
@require_http_methods(["GET", "POST"])
def upload_pdf(request):
    """
    Lida com o upload do arquivo. Se for POST, atua como proxy para a API externa,
    salvando o texto extraído na sessão.
    """
    success_message = None
    error_message = None

    if request.method == 'POST':
        if 'file' in request.FILES:
            uploaded_file = request.FILES['file']
            
            # Prepara os dados para o proxy
            files = {'file': (uploaded_file.name, uploaded_file.file.read(), uploaded_file.content_type)}
            
            # === PASSO 1: ENVIAR PARA A API EXTERNA VIA PROXY (EVITA CORS/CSRF) ===
            try:
                # O Django envia a requisição POST diretamente para a API externa
                response = requests.post(f"{EXTERNAL_API_URL}/", files=files, timeout=30)
                
                # Verifica se a API externa respondeu com sucesso
                if response.status_code == 200:
                    data = response.json()
                    extracted_text = data.get('extracted_text')
                    
                    if extracted_text:
                        # Salva o texto extraído na sessão para uso futuro pela IA
                        request.session['extracted_text'] = extracted_text
                        success_message = f"✅ Currículo processado ({uploaded_file.name}). Agora utilize as ferramentas de IA."
                    else:
                        error_message = f"❌ API externa não retornou o texto extraído. Resposta: {data.get('error', 'Sem detalhe.')}"
                else:
                    error_message = f"❌ Falha no processamento pela API externa. Status: {response.status_code}. Detalhes: {response.text}"

            except requests.exceptions.RequestException as e:
                # Trata erros de rede (timeout, conexão, etc.)
                error_message = f"❌ Erro de conexão com o servidor externo: {e}"
            
            # Após o processamento (sucesso ou falha), o formulário redireciona para evitar re-submissão
            # e carrega a página novamente com as mensagens de feedback
            request.session['success'] = success_message
            request.session['error'] = error_message
            return redirect('upload_route') 
        else:
            error_message = "❌ Nenhum arquivo encontrado no formulário."
            
    # Mensagens e contexto para o render (após GET ou redirect POST)
    if 'success' in request.session:
        success_message = request.session.pop('success')
    if 'error' in request.session:
        error_message = request.session.pop('error')
        
    extracted_text = request.session.get('extracted_text', '')

    context = {
        'success': success_message,
        'error': error_message,
        'extracted_text': extracted_text, # Passa o texto para o JavaScript via template
    }

    return render(request, 'upload.html', context)


# ==============================================================================
# VIEW PARA AS PERGUNTAS À IA (AJAX)
# Rota: /ask/ (name='ask_rag')
# ==============================================================================
@require_http_methods(["POST"])
def ask_rag(request):
    """
    Recebe uma pergunta via AJAX, combina com o currículo da sessão
    e envia para a API externa via proxy.
    """
    # 1. Checa o CSRF e garante que é JSON (o decorador @csrf_exempt NÃO é necessário aqui)
    try:
        data = json.loads(request.body)
        user_question = data.get('q')
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Requisição JSON inválida.'}, status=400)
    
    extracted_text = request.session.get('extracted_text')

    if not extracted_text:
        return JsonResponse({'error': 'Nenhum currículo processado. Por favor, envie o documento primeiro.'}, status=400)
    
    if not user_question:
        return JsonResponse({'error': 'Nenhuma pergunta fornecida.'}, status=400)

    # Constrói o prompt para a IA (contexto + pergunta)
    full_prompt = f"Com base no currículo abaixo, responda à pergunta: '{user_question}'.\n\nCURRÍCULO:\n{extracted_text}"
    
    # === PASSO 2: ENVIAR PERGUNTA PARA A API EXTERNA VIA PROXY ===
    try:
        # Envia a requisição POST diretamente para a API externa
        response = requests.post(
            f"{EXTERNAL_API_URL}/ask/",
            json={'q': full_prompt}, # Envia o prompt completo no corpo JSON
            timeout=60 # Aumenta o timeout para respostas da IA
        )
        
        # Verifica se a API externa respondeu com sucesso
        if response.status_code == 200:
            api_data = response.json()
            return JsonResponse({'answer': api_data.get('answer', 'A IA não forneceu uma resposta.')})
        else:
            return JsonResponse({'error': f"API externa falhou com status {response.status_code}. Detalhes: {response.text}"}, status=response.status_code)

    except requests.exceptions.RequestException as e:
        return JsonResponse({'error': f"Erro de conexão com o servidor de IA: {e}"}, status=503)