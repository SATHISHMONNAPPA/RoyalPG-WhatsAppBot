import os
import logging
from twilio.rest import Client
from twilio.base.exceptions import TwilioException

logger = logging.getLogger(__name__)

class TwilioService:
    def __init__(self):
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.from_number = os.getenv("TWILIO_PHONE_NUMBER")

        if not all([self.account_sid, self.auth_token, self.from_number]):
            raise ValueError("Twilio environment variables are missing")

        self.client = Client(self.account_sid, self.auth_token)

    def send_message(self, to_phone_number, message_body):
        try:
            if not to_phone_number.startswith("whatsapp:"):
                to_phone_number = f"whatsapp:{to_phone_number}"

            if to_phone_number == self.from_number:
                logger.error("Cannot send message to the same number as the sender")
                return False

            message = self.client.messages.create(
                body=message_body,
                from_=self.from_number,
                to=to_phone_number
            )
            logger.info(f"Message SID: {message.sid}")
            return True
        except TwilioException as e:
            logger.error(f"Twilio error: {e}")
            return False

    def send_rate_limit_message(self, to_phone_number):
        rate_limit_msg = (
            "You've reached the message limit. Please wait before sending another message."
        )
        return self.send_message(to_phone_number, rate_limit_msg)
