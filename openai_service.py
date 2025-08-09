# openai_service.py
import os
import logging
from openai import OpenAI

logging.basicConfig(level=logging.INFO)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class OpenAIService:
    def __init__(self):
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY not set in environment variables")

    def generate_response(self, user_message):
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant for Royal PG."},
                    {"role": "user", "content": user_message}
                ]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logging.error(f"Error generating AI response: {e}")
            return "Sorry, I couldn't process your message at the moment."
