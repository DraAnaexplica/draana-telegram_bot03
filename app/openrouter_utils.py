import os
import requests
import logging

logger = logging.getLogger("draana.openrouter_utils")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "").strip()
OPENROUTER_URL = os.getenv("OPENROUTER_URL", "https://api.openrouter.ai/v1/chat/completions")

def gerar_resposta_openrouter(historico: list[dict]) -> str:
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {"model": "gpt-4o-mini", "messages": historico}
    try:
        resp = requests.post(OPENROUTER_URL, json=payload, headers=headers, timeout=20)
        resp.raise_for_status()
        data = resp.json()
        choice = data.get("choices", [])[0]
        return choice.get("message", {}).get("content", "").strip()
    except Exception as e:
        logger.error(f"Erro OpenRouter: {e}")
        return "Desculpe, houve um erro ao processar sua mensagem."  