import os
from dotenv import load_dotenv

load_dotenv()

# Variáveis internas (iniciam vazias)
_llm = None
_emb = None
_vectordb = None


def get_llm():
    """
    Inicia a LLM apenas quando necessário.
    """
    global _llm
    if _llm is None:
        # Importação movida para cá para não travar o servidor
        from langchain_openai import ChatOpenAI
        _llm = ChatOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            model="gpt-4o-mini",
            temperature=0.3
        )
    return _llm


def get_embedding():
    """
    Inicia Embeddings apenas quando necessário.
    """
    global _emb
    if _emb is None:
        from langchain_openai import OpenAIEmbeddings
        _emb = OpenAIEmbeddings(
            api_key=os.getenv("OPENAI_API_KEY")
        )
    return _emb


def get_vectordb():
    """
    Inicia o Banco Vetorial (Chroma) apenas quando necessário.
    Esta é a importação mais pesada que costuma travar o Django.
    """
    global _vectordb
    if _vectordb is None:
        from langchain_chroma import Chroma

        emb = get_embedding()
        # Garante que o diretório existe e conecta nele
        persist_directory = "vector_db"

        _vectordb = Chroma(
            persist_directory=persist_directory,
            embedding_function=emb
        )
    return _vectordb


def rag_query(question: str):
    """
    Função principal de busca e resposta.
    """
    # Carrega os objetos agora (Lazy Load)
    vectordb = get_vectordb()
    llm = get_llm()

    # Busca contexto (5 trechos mais relevantes)
    docs = vectordb.similarity_search(question, k=5)
    context = "\n\n".join([d.page_content for d in docs])

    if not context:
        context = "Nenhuma informação relevante encontrada nos documentos enviados."

    prompt = f"""
    ATUE COMO: Um Especialista Sênior em Recrutamento e ATS.

    CONTEXTO DO DOCUMENTO:
    {context}

    PERGUNTA: {question}

    RESPOSTA PROFISSIONAL (Use Markdown):
    """

    answer = llm.invoke(prompt)
    return answer.content