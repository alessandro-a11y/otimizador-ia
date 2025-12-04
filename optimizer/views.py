from django.shortcuts import render
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
import json
# from .utils import extract_text_from_file # Certifique-se de importar sua função real de utilidade

def upload_interface_and_process(request):
    success_message = request.session.pop('success', None)
    error_message = request.session.pop('error', None)
    extracted_text = request.session.get('extracted_text', '')

    if request.method == 'POST':
        if 'file' in request.FILES:
            uploaded_file = request.FILES['file']
            
            try:
                # Substitua esta simulação pela sua função real de extração
                text = f"Texto extraído de {uploaded_file.name}. Este é o conteúdo que será usado pela IA." 
                
                request.session['extracted_text'] = text
                request.session['success'] = f"✅ Sucesso! '{uploaded_file.name}' processado. Agora você pode perguntar à IA."
                
                return HttpResponseRedirect(reverse('upload_interface')) 

            except Exception as e:
                request.session['error'] = f"❌ Erro ao processar o arquivo: {str(e)}"
                return HttpResponseRedirect(reverse('upload_interface')) 
        else:
            request.session['error'] = "❌ Nenhum arquivo enviado."
            return HttpResponseRedirect(reverse('upload_interface'))

    context = {
        'extracted_text': extracted_text,
        'success': success_message,
        'error': error_message,
    }
    
    return render(request, 'upload.html', context)


def ask_rag_api(request):
    if request.method == 'POST':
        extracted_text = request.session.get('extracted_text', '')
        if not extracted_text:
            return JsonResponse({'error': 'Nenhum currículo processado. Faça o upload primeiro.'}, status=400)

        try:
            data = json.loads(request.body)
            question = data.get('q', '').strip()
            
            # Substitua esta simulação pela sua lógica de IA real
            answer = f"Resposta da IA para a pergunta '{question}': O currículo menciona 5 anos de experiência e as habilidades em Python e Django."
            
            return JsonResponse({'answer': answer})
        except Exception as e:
            return JsonResponse({'error': f'Erro na comunicação com a IA: {str(e)}'}, status=500)
    
    return JsonResponse({'error': 'Método não permitido.'}, status=405)