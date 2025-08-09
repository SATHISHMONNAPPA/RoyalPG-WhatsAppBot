# app.py
import logging
from flask import Flask, request, jsonify
from werkzeug.middleware.proxy_fix import ProxyFix
from openai_service import OpenAIService
from twilio_service import TwilioService
from rate_limiter import RateLimiter
from config import SECRET_KEY, RATE_LIMIT_PER_MINUTE

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.secret_key = SECRET_KEY
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Initialize services
try:
    openai_service = OpenAIService()
    twilio_service = TwilioService()
    rate_limiter = RateLimiter(max_requests_per_minute=RATE_LIMIT_PER_MINUTE)
    logger.info("All services initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize services: {str(e)}")
    openai_service = None
    twilio_service = None
    rate_limiter = None

@app.route('/')
def home():
    """Health check endpoint."""
    return jsonify({
        "status": "running",
        "service": "Royal PG WhatsApp Bot",
        "message": "Bot is ready to handle WhatsApp messages"
    })

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle incoming WhatsApp messages from Twilio."""
    try:
        if not all([openai_service, twilio_service, rate_limiter]):
            logger.error("Services not properly initialized")
            return jsonify({"error": "Service unavailable"}), 500

        incoming_msg = request.form.get('Body', '').strip()
        from_number = request.form.get('From', '')   # User's number
        to_number = request.form.get('To', '')       # Your Twilio sandbox number

        logger.info(f"Received message from {from_number}: {incoming_msg}")

        if not incoming_msg or not from_number:
            logger.warning("Missing required fields in webhook request")
            return jsonify({"error": "Missing required fields"}), 400

        # Rate limiting
        phone_number = from_number.replace('whatsapp:', '')
        if not rate_limiter.is_allowed(phone_number):
            logger.warning(f"Rate limit exceeded for {phone_number}")
            twilio_service.send_rate_limit_message(from_number)
            return jsonify({"status": "rate_limited"}), 200

        # Short welcome message for very short inputs
        if len(incoming_msg) < 2:
            welcome_msg = (
                "Hello! 👋 Welcome to Royal PG. I'm here to help with information about "
                "our accommodation facilities near Oxford and Dayananda Sagar Engineering Colleges. "
                "Ask me about rooms, pricing, facilities, or location!"
            )
            twilio_service.send_message(from_number, welcome_msg)
            return jsonify({"status": "welcome_sent"}), 200

        # Generate AI response
        ai_response = openai_service.generate_response(incoming_msg)

        # Send back to sender
        success = twilio_service.send_message(from_number, ai_response)

        if success:
            logger.info(f"Response sent successfully to {from_number}")
            return jsonify({"status": "message_sent"}), 200
        else:
            logger.error(f"Failed to send response to {from_number}")
            return jsonify({"error": "Failed to send response"}), 500

    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/status')
def status():
    """Service health check."""
    service_status = {
        "openai_service": openai_service is not None,
        "twilio_service": twilio_service is not None,
        "rate_limiter": rate_limiter is not None
    }
    return jsonify({
        "status": "healthy" if all(service_status.values()) else "degraded",
        "services": service_status,
        "rate_limit_per_minute": RATE_LIMIT_PER_MINUTE
    }), 200 if all(service_status.values()) else 503

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

if __name__ == '__main__':
    logger.info("Starting Royal PG WhatsApp Bot server...")
    app.run(host='0.0.0.0', port=5000, debug=True)
