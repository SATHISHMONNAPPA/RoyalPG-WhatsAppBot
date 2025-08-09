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

# Flask App
app = Flask(__name__)
app.secret_key = SECRET_KEY
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Initialize Services
try:
    openai_service = OpenAIService()
    twilio_service = TwilioService()
    rate_limiter = RateLimiter(max_requests_per_minute=RATE_LIMIT_PER_MINUTE)
    logger.info("All services initialized successfully")
except Exception as e:
    logger.error(f"Service init failed: {e}")
    openai_service = None
    twilio_service = None
    rate_limiter = None

@app.route('/')
def home():
    return jsonify({
        "status": "running",
        "service": "Royal PG WhatsApp Bot",
        "message": "Bot is ready to handle WhatsApp messages"
    })

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        if not all([openai_service, twilio_service, rate_limiter]):
            return jsonify({"error": "Service unavailable"}), 500

        incoming_msg = request.form.get('Body', '').strip()
        from_number = request.form.get('From', '')
        
        logger.info(f"Message from {from_number}: {incoming_msg}")

        if not incoming_msg or not from_number:
            return jsonify({"error": "Missing fields"}), 400

        phone_number = from_number.replace('whatsapp:', '')

        if not rate_limiter.is_allowed(phone_number):
            twilio_service.send_rate_limit_message(from_number)
            return jsonify({"status": "rate_limited"}), 200

        if len(incoming_msg) < 2:
            welcome_msg = (
                "Hello! 👋 Welcome to Royal PG. Ask me about rooms, pricing, facilities, or location."
            )
            twilio_service.send_message(from_number, welcome_msg)
            return jsonify({"status": "welcome_sent"}), 200

        ai_response = openai_service.generate_response(incoming_msg)
        success = twilio_service.send_message(from_number, ai_response)

        if success:
            return jsonify({"status": "message_sent"}), 200
        else:
            return jsonify({"error": "Failed to send"}), 500

    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/status')
def status():
    return jsonify({
        "status": "healthy" if all([openai_service, twilio_service, rate_limiter]) else "degraded"
    })

if __name__ == '__main__':
    logger.info("Starting Royal PG WhatsApp Bot server...")
    app.run(host='0.0.0.0', port=5000, debug=True)
