import os
import logging
import requests

logger = logging.getLogger(__name__)
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

class OpenAIService:
    def __init__(self):
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required")
        self.api_key = OPENAI_API_KEY
        self.base = "https://api.openai.com/v1"

    def generate_response(self, user_message: str, model: str="gpt-3.5-turbo") -> str:
        try:
            url = f"{self.base}/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant for Royal PG. Keep replies short and helpful."},
                    {"role": "user", "content": user_message}
                ],
                "max_tokens": 300,
                "temperature": 0.7
            }
            resp = requests.post(url, json=payload, headers=headers, timeout=15)
            if resp.status_code != 200:
                logger.error("OpenAI HTTP status error: %s - %s", resp.status_code, resp.text)
                return "Sorry, I'm having trouble answering right now."
            j = resp.json()
            try:
                return j["choices"][0]["message"]["content"].strip()
            except Exception:
                logger.error("Unexpected OpenAI response format: %s", j)
                return "Sorry, I couldn't form a reply."
        except Exception as e:
            logger.exception("Error generating AI response:")
            return "Sorry, I'm experiencing a technical issue."
