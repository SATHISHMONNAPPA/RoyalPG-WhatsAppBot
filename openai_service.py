# openai_service.py
import os
import logging
import json
from typing import Optional

# We'll try to use the official OpenAI client if available,
# but we will NOT create it at import time to avoid startup crashes.
try:
    from openai import OpenAI  # type: ignore
    _HAS_OPENAI_SDK = True
except Exception:
    _HAS_OPENAI_SDK = False

import httpx  # httpx is already in your requirements.txt

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class OpenAIService:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        self._client = None  # lazy-initialized OpenAI client

    def _init_client(self) -> Optional["OpenAI"]:
        """
        Lazily initialize the official OpenAI client. If initialization fails,
        return None and rely on httpx fallback.
        """
        if self._client is not None:
            return self._client

        if not _HAS_OPENAI_SDK:
            logger.warning("OpenAI SDK not installed / import failed. Will use HTTP fallback.")
            return None

        try:
            # Create the official OpenAI client here (lazy)
            self._client = OpenAI(api_key=self.api_key)
            return self._client
        except Exception as e:
            # If any error occurs during client creation, log and fallback to httpx
            logger.error(f"Failed to initialize OpenAI SDK client: {e}")
            self._client = None
            return None

    def generate_response(self, user_message: str) -> str:
        """
        Generate a response using the OpenAI Chat Completions API.
        Tries the official SDK first (if available), then falls back to HTTP.
        """
        system_prompt = (
            "You are a helpful assistant for Royal PG. Provide concise, friendly answers about rooms, pricing, "
            "facilities, location and booking. If asked about booking, ask them to call +91-9876543210."
        )

        # First try the SDK (if available)
        client = self._init_client()
        if client:
            try:
                resp = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message}
                    ],
                    temperature=0.7,
                    max_tokens=500
                )
                # Compatible with new SDK response shape
                return resp.choices[0].message.content.strip()
            except Exception as e:
                logger.error(f"OpenAI SDK call failed: {e} — falling back to REST HTTP call.")

        # Fallback: call OpenAI REST API directly using httpx
        try:
            url = "https://api.openai.com/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                "temperature": 0.7,
                "max_tokens": 500
            }

            with httpx.Client(timeout=30.0) as http_client:
                r = http_client.post(url, headers=headers, json=payload)
                r.raise_for_status()
                data = r.json()
                # Safely extract the text
                choice = data.get("choices", [{}])[0]
                message = choice.get("message", {}) or choice.get("text") or ""
                # If message is a dict with 'content'
                if isinstance(message, dict):
                    content = message.get("content", "")
                else:
                    content = message
                content = (content or "").strip()
                if content:
                    return content
                else:
                    logger.error("OpenAI HTTP response contained no usable text.")
                    return "Sorry — I couldn't generate a response. Please try again later."
        except httpx.HTTPStatusError as e:
            logger.error(f"OpenAI HTTP status error: {e.response.status_code} - {e.response.text}")
            return "Sorry, I'm having trouble accessing the AI service right now."
        except Exception as e:
            logger.error(f"OpenAI HTTP request failed: {e}")
            return "Sorry, I'm having trouble accessing the AI service right now."
