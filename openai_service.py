import os
import logging
from typing import List, Dict, Any
import openai
from config import OPENAI_API_KEY, ROYAL_PG_INFO

logger = logging.getLogger(__name__)

class OpenAIService:
    def __init__(self):
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY environment variable is required")

        openai.api_key = OPENAI_API_KEY
        self.system_prompt = self._create_system_prompt()
    
    def _create_system_prompt(self):
        return f"""
You are a helpful customer service assistant for Royal PG, a premium accommodation facility in Bangalore. 
Your role is to assist potential residents with inquiries about rooms, facilities, pricing, and location.

IMPORTANT GUIDELINES:
1. Always be polite, professional, and helpful
2. Provide accurate information based on the details below
3. If asked about something not covered in the information, politely say you'll connect them with management
4. Encourage interested prospects to visit or call for booking
5. Keep responses concise but informative
6. Use a friendly, conversational tone suitable for students and professionals

ROYAL PG INFORMATION:
{ROYAL_PG_INFO}

Remember to:
- Answer questions about room types, pricing, and facilities accurately
- Highlight the proximity to engineering colleges when relevant
- Mention the comprehensive facilities included in the rent
- Provide contact information when requested
- Encourage visits for better understanding of the facilities

If someone asks about booking or availability, direct them to call +91-9876543210 or visit the premises.
"""

    def generate_response(self, user_message: str, conversation_history: List[Dict[str, Any]] = None) -> str:
        try:
            messages: List[Dict[str, str]] = [{"role": "system", "content": self.system_prompt}]
            
            if conversation_history:
                messages.extend(conversation_history)
            
            messages.append({"role": "user", "content": user_message})

            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content
            if ai_response:
                ai_response = ai_response.strip()
                logger.info(f"Generated AI response: {ai_response[:100]}...")
                return ai_response
            else:
                logger.warning("Empty response from OpenAI")
                return "I'm sorry, I couldn't generate a proper response. Please try again or contact Royal PG directly."
        
        except Exception as e:
            logger.error(f"Error generating AI response: {str(e)}")
            return ("I apologize, but I'm experiencing technical difficulties. "
                   "Please contact Royal PG directly at +91-9876543210 for immediate assistance.")
