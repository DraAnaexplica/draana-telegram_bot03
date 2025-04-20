# app/openrouter_utils.py

import os
import requests
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = "deepseek/deepseek-chat-v3-0324"  # ou troque pelo que desejar

def gerar_resposta_openrouter(mensagens):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://draana.onrender.com",
        "X-Title": "DraAnaTelegramBot"
    }

    # Carrega o system prompt do arquivo
    with open("app/system_prompt.txt", "r", encoding="utf-8") as f:
        system_prompt = f.read().strip()

    # Adiciona o system prompt como primeira mensagem
    mensagens.insert(0, {"role": "system", "content": system_prompt})

    data = {
        "model": MODEL,
        "messages": mensagens,
        "temperature": 0.8
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        print(f"Erro ao gerar resposta: {e}")
        return "Desculpe, algo deu errado ao gerar a resposta."
