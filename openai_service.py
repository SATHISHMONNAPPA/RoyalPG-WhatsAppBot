# openai_service.py

import os
from openai import OpenAI
import logging

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_ai_response(user_message):
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
