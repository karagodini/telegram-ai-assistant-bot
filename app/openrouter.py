import httpx

API_URL = "https://openrouter.ai/api/v1/chat/completions"


async def chat(messages: list[dict], model: str, api_key: str) -> str:
    """Диалог с LLM через OpenRouter-совместимый API."""
    headers = {"Authorization": f"Bearer {api_key}"}
    payload = {"model": model, "messages": messages}
    async with httpx.AsyncClient(timeout=90) as client:
        resp = await client.post(API_URL, json=payload, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"].strip()
