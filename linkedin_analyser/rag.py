import os
from dotenv import load_dotenv

load_dotenv()

# Variáveis internas globais (iniciam vazias)
_llm = None
_emb = None
_vectordb = None


def get_llm():
    """
    Inicia a LLM (Cérebro) apenas quando necessário.
    A importação é feita aqui dentro para não travar o arranque do Django.
    """
    global _llm
    if _llm is None:
        from langchain_openai import ChatOpenAI
        _llm = ChatOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            model="gpt-4o-mini",
            temperature=0.4  # Temperatura ajustada para criatividade moderada
        )
    return _llm


def get_embedding():
    """
    Inicia os Embeddings apenas quando necessário.
    """
    global _emb
    if _emb is None:
        from langchain_openai import OpenAIEmbeddings
        _emb = OpenAIEmbeddings(api_key=os.getenv("OPENAI_API_KEY"))
    return _emb


def get_vectordb():
    """
    Inicia o Banco Vetorial específico do LinkedIn apenas quando necessário.
    """
    global _vectordb
    if _vectordb is None:
        from langchain_chroma import Chroma

        emb = get_embedding()
        # Usa diretório separado 'vector_db_linkedin' para não misturar com currículos
        _vectordb = Chroma(
            persist_directory="vector_db_linkedin",
            embedding_function=emb
        )
    return _vectordb


def analyze_linkedin_profile(question: str):
    """
    Função principal que processa a pergunta sobre o perfil do LinkedIn.
    """
    # Carrega os objetos de IA sob demanda (Lazy Load) agora que precisamos deles
    llm = get_llm()
    vectordb = get_vectordb()

    # Busca contexto relevante no banco
    docs = vectordb.similarity_search(question, k=6)
    context = "\n\n".join([d.page_content for d in docs])

    if not context:
        context = "Não foi possível ler o conteúdo do perfil enviado. O arquivo pode estar vazio ou ser uma imagem não processada."

    # Prompt especialista para LinkedIn
    prompt = f"""
    ATUE COMO: Um 'LinkedIn Top Voice' e Especialista em Personal Branding e Recrutamento.

    SUA MISSÃO: Transformar o perfil do usuário em um ímã de oportunidades de emprego.

    CONTEXTO DO PERFIL (Extraído do PDF):
    {context}

    PERGUNTA DO USUÁRIO:
    {question}

    DIRETRIZES DE RESPOSTA:
    1. Seja direto, estratégico e use linguagem corporativa moderna.
    2. Se o usuário pedir sobre o Headline, foque em palavras-chave de busca.
    3. Se pedir sobre o Sobre/Resumo, verifique storytelling e ganchos iniciais.
    4. Se pedir nota, seja rigoroso (0-100) simulando o SSI do LinkedIn.
    5. Use Markdown e Emojis para deixar a leitura agradável.

    SUA CONSULTORIA:
    """

    answer = llm.invoke(prompt)
    return answer.content