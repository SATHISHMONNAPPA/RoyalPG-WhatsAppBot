import os
import logging
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

logger = logging.getLogger(__name__)

TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.environ.get("TWILIO_PHONE_NUMBER", "whatsapp:+14155238886")
# Allow sending to same number for testing (default False)
ALLOW_SEND_TO_SELF = os.environ.get("ALLOW_SEND_TO_SELF", "false").lower() in ("1","true","yes")

class TwilioService:
    def __init__(self):
        if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
            raise ValueError("Twilio credentials are required")
        self.client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        self.from_number = TWILIO_PHONE_NUMBER

    def send_message(self, to_phone_number: str, message_body: str) -> bool:
        try:
            if not to_phone_number.startswith("whatsapp:"):
                to_phone_number = f"whatsapp:{to_phone_number}"

            if (to_phone_number == self.from_number) and (not ALLOW_SEND_TO_SELF):
                logger.error("Cannot send message to the same number as the sender")
                return False

            msg = self.client.messages.create(
                body=message_body,
                from_=self.from_number,
                to=to_phone_number
            )
            logger.info("Twilio Message SID: %s", getattr(msg, "sid", "<no-sid>"))
            return True
        except TwilioRestException as e:
            logger.error("Twilio error: %s", e)
            return False
        except Exception as e:
            logger.exception("Unexpected Twilio error:")
            return False

    def send_rate_limit_message(self, to_phone_number: str) -> bool:
        rate_msg = "You've hit the limit. Please wait a moment and try again. For urgent help call +91-9876543210."
        return self.send_message(to_phone_number, rate_msg)
