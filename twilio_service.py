# twilio_service.py

import logging
from twilio.rest import Client
from twilio.base.exceptions import TwilioException
from config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER

logger = logging.getLogger(__name__)

class TwilioService:
    def __init__(self):
        if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
            raise ValueError("TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN are required")

        self.client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        self.from_number = TWILIO_PHONE_NUMBER

    def send_message(self, to_phone_number, message_body):
        """
        Send a WhatsApp message to the specified phone number.

        Args:
            to_phone_number (str): Recipient's phone number with whatsapp: prefix
            message_body (str): Message to send
        """
        try:
            # Ensure correct format
            if not to_phone_number.startswith('whatsapp:'):
                to_phone_number = f"whatsapp:{to_phone_number}"

            # Prevent sending message to self (Twilio sandbox number)
            if to_phone_number == self.from_number:
                logger.error("Attempted to send a message to the Twilio sandbox number itself. Aborting.")
                return False

            message = self.client.messages.create(
                body=message_body,
                from_=self.from_number,
                to=to_phone_number
            )

            logger.info(f"Message sent successfully to {to_phone_number}. SID: {message.sid}")
            return True

        except TwilioException as e:
            logger.error(f"Twilio error sending message: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending message: {str(e)}")
            return False

    def send_rate_limit_message(self, to_phone_number):
        """Send a rate limit notification message."""
        msg = (
            "⏳ You've reached the message limit. Please wait a minute before sending another message.\n"
            "For urgent inquiries, call 📞 +91-9876543210 directly."
        )
        return self.send_message(to_phone_number, msg)
