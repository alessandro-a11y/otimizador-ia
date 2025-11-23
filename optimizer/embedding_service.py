from openai import OpenAI
import numpy as np
from django.conf import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)

def generate_embedding(text: str):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return np.array(response.data[0].embedding, dtype=np.float32).tobytes()
