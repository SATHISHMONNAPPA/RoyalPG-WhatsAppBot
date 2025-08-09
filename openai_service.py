# openai_service.py

import os
import logging
from openai import OpenAI

logger = logging.getLogger(__name__)

class OpenAIService:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        self.client = OpenAI(api_key=api_key)

    def generate_response(self, user_message):
        """
        Generate an AI response using OpenAI's Chat Completions API.

        Args:
            user_message (str): The user's message text.

        Returns:
            str: AI-generated response text.
        """
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",  # You can change to gpt-4 if available
                messages=[
                    {"role": "system", "content": "You are a helpful assistant for Royal PG. Provide concise and clear answers about our PG, rooms, pricing, facilities, and location."},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7,
                max_tokens=500
            )

            ai_message = response.choices[0].message.content.strip()
            logger.info(f"Generated AI response: {ai_message}")
            return ai_message

        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            return "Sorry, I couldn't process your message right now. Please try again later."
