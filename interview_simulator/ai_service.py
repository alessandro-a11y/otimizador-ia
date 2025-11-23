import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente (Leve)
load_dotenv()


# --- FUNÇÕES COM IMPORTS TARDIO (LAZY LOADING) ---
# As bibliotecas pesadas (OpenAI, LangChain, Chroma) só são carregadas
# quando a função é chamada, evitando travar o Django na inicialização.

def get_openai_client():
    from openai import OpenAI
    return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def transcribe_audio(file_path):
    """
    Usa o modelo Whisper para converter áudio em texto.
    """
    try:
        client = get_openai_client()
        with open(file_path, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language="pt"
            )
        return transcription.text
    except Exception as e:
        print(f"Erro no Whisper: {e}")
        return "Erro ao transcrever áudio."


def analyze_answer(question, transcript):
    """
    Analisa a resposta do candidato usando GPT-4o.
    """
    try:
        client = get_openai_client()
        prompt = f"""
        ATUE COMO: Um Entrevistador Sênior.
        PERGUNTA FEITA: "{question}"
        RESPOSTA DO CANDIDATO: "{transcript}"

        SUA MISSÃO: Avalie a resposta em 3 pilares:
        1. CLAREZA E POSTURA
        2. CONTEÚDO TÉCNICO
        3. MELHORIA (Reescreva a resposta ideal)

        Dê também uma nota de 0 a 10. SAÍDA EM MARKDOWN.
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Erro na análise: {str(e)}"


def generate_question(job_context_text="", industry_type="Geral"):
    """
    Gera uma pergunta. Conecta no VectorDB manualmente e gera prompt.
    """
    resume_context = ""

    # --- ACESSO AO BANCO DE DADOS (LAZY) ---
    try:
        # Importações pesadas movidas para cá
        from langchain_openai import OpenAIEmbeddings
        from langchain_chroma import Chroma

        # 1. Configura Embeddings
        emb = OpenAIEmbeddings(api_key=os.getenv("OPENAI_API_KEY"))

        # 2. Conecta na pasta 'vector_db' se ela existir
        if os.path.exists("vector_db"):
            vectordb = Chroma(
                persist_directory="vector_db",
                embedding_function=emb
            )
            docs = vectordb.similarity_search("experiência profissional habilidades", k=3)
            resume_context = "\n".join([d.page_content for d in docs])
    except Exception as e:
        print(f"Aviso: Não foi possível ler o banco de currículos ({e})")
    # ---------------------------------------

    try:
        client = get_openai_client()
        prompt_user = f"""
        Recrutador do setor: {industry_type}.

        CONTEXTO DA VAGA:
        {job_context_text[:2000] if job_context_text else "Nenhum contexto específico."}

        PERFIL DO CANDIDATO:
        {resume_context[:2000] if resume_context else "Desconhecido."}

        TAREFA: Gere APENAS UMA pergunta de entrevista difícil e técnica. Curta e direta.
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt_user}],
            temperature=0.8
        )
        return response.choices[0].message.content
    except Exception as e:
        return "Conte-me sobre um desafio profissional que você superou."


def generate_speech(text):
    """
    Gera áudio (TTS) a partir de um texto.
    """
    try:
        client = get_openai_client()
        response = client.audio.speech.create(
            model="tts-1",
            voice="onyx",
            input=text
        )
        return response.content
    except Exception as e:
        print(f"Erro no TTS: {e}")
        return None