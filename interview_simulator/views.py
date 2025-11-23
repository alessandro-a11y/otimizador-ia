from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage
from .ai_service import transcribe_audio, analyze_answer, generate_question, generate_speech
import os
import base64

# --- MUDANÇA CRÍTICA: Importamos do utils LOCAL (.utils) ---
# Isso evita depender do app 'optimizer' e previne erros de inicialização.
from .utils import extract_text


def setup_page(request):
    """
    ETAPA 1: Página de Configuração.
    Define o setor e carrega o contexto da vaga (texto ou arquivo).
    """
    if request.method == "POST":
        industry = request.POST.get('industry', 'Geral')
        job_text = request.POST.get('job_text', '')

        # Se o usuário subiu um arquivo (PDF/IMG do Edital)
        if request.FILES.get('job_file'):
            try:
                uploaded_file = request.FILES['job_file']
                fs = FileSystemStorage()
                filename = fs.save(f"setup_{uploaded_file.name}", uploaded_file)
                file_path = fs.path(filename)

                # Usa a função local para extrair texto
                extracted = extract_text(file_path)
                job_text += "\n" + extracted

                # Limpa o arquivo temporário
                os.remove(file_path)
            except Exception as e:
                print(f"Erro ao processar arquivo da vaga: {e}")

        # Salva na sessão para a próxima etapa
        request.session['industry'] = industry
        request.session['job_context'] = job_text[:5000]

        return redirect('interview_start')

    return render(request, 'interview_simulator/setup.html')


def interview_page(request):
    """
    ETAPA 2: A Entrevista.
    Recupera o contexto e inicia a câmera.
    """
    industry = request.session.get('industry', 'Geral')
    job_context = request.session.get('job_context', '')

    # Gera a primeira pergunta
    initial_question = generate_question(job_context, industry)

    # Gera o áudio (TTS)
    audio_content = generate_speech(initial_question)
    audio_b64 = ""
    if audio_content:
        audio_b64 = base64.b64encode(audio_content).decode('utf-8')

    return render(request, 'interview_simulator/interview.html', {
        'question': initial_question,
        'audio_base64': audio_b64,
        'industry': industry
    })


@csrf_exempt
def get_new_question(request):
    """
    API para gerar nova pergunta via AJAX.
    """
    industry = request.session.get('industry', 'Geral')
    job_context = request.session.get('job_context', '')

    question = generate_question(job_context, industry)

    audio_content = generate_speech(question)
    audio_b64 = ""
    if audio_content:
        audio_b64 = base64.b64encode(audio_content).decode('utf-8')

    return JsonResponse({'question': question, 'audio_base64': audio_b64})


@csrf_exempt
def analyze_response(request):
    """
    API para receber o áudio da resposta e analisar via IA.
    """
    if request.method == 'POST' and request.FILES.get('audio_data'):
        try:
            audio_file = request.FILES['audio_data']
            current_question = request.POST.get('question_text', '')

            fs = FileSystemStorage()
            filename = fs.save(f"interview_temp_{audio_file.name}.webm", audio_file)
            file_path = fs.path(filename)

            # Transcreve (Whisper)
            transcript = transcribe_audio(file_path)

            # Analisa (GPT)
            feedback = analyze_answer(current_question, transcript)

            # Limpeza
            try:
                os.remove(file_path)
            except:
                pass

            return JsonResponse({'transcript': transcript, 'feedback': feedback})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Nenhum áudio recebido'}, status=400)