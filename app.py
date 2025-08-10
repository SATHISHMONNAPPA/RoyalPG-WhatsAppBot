import logging
import os
from flask import Flask, request, jsonify
from werkzeug.middleware.proxy_fix import ProxyFix
from config import SECRET_KEY, RATE_LIMIT_PER_MINUTE
from openai_service import OpenAIService
from twilio_service import TwilioService
from rate_limiter import RateLimiter

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = SECRET_KEY
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# initialize safely
openai_service = None
twilio_service = None
rate_limiter = None

try:
    openai_service = OpenAIService()
    twilio_service = TwilioService()
    rate_limiter = RateLimiter(max_requests_per_minute=RATE_LIMIT_PER_MINUTE)
    logger.info("All services initialized successfully")
except Exception as e:
    logger.exception("Service init failed: %s", e)

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status":"running","service":"Royal PG WhatsApp Bot"})

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        if not all([openai_service, twilio_service, rate_limiter]):
            logger.error("Services not initialized")
            return jsonify({"error":"service_unavailable"}), 503

        incoming_msg = request.form.get("Body", "").strip()
        from_number = request.form.get("From", "")
        to_number = request.form.get("To", "")

        logger.info("Message from %s: %s", from_number, incoming_msg)

        if not incoming_msg or not from_number:
            return jsonify({"error":"missing_fields"}), 400

        phone = from_number.replace("whatsapp:", "")

        if not rate_limiter.is_allowed(phone):
            logger.warning("Rate limited %s", phone)
            twilio_service.send_rate_limit_message(from_number)
            return jsonify({"status":"rate_limited"}), 200

        if len(incoming_msg) < 2:
            welcome = ("Hello! 👋 Welcome to Royal PG. Ask about rooms, pricing, facilities or location.")
            twilio_service.send_message(from_number, welcome)
            return jsonify({"status":"welcome_sent"}), 200

        ai_response = openai_service.generate_response(incoming_msg)
        ok = twilio_service.send_message(from_number, ai_response)
        if ok:
            return jsonify({"status":"message_sent"}), 200
        else:
            return jsonify({"error":"send_failed"}), 500

    except Exception as e:
        logger.exception("Webhook error:")
        return jsonify({"error":"internal_error"}), 500

@app.route("/test", methods=["POST"])
def test():
    data = request.get_json(force=True)
    if not data or "message" not in data:
        return jsonify({"error":"message_required"}), 400
    msg = data["message"]
    if not openai_service:
        return jsonify({"error":"openai_unavailable"}), 503
    resp = openai_service.generate_response(msg)
    return jsonify({"user":msg,"ai":resp})

@app.route("/status", methods=["GET"])
def status():
    services = {
        "openai_service": openai_service is not None,
        "twilio_service": twilio_service is not None,
        "rate_limiter": rate_limiter is not None
    }
    status = "healthy" if all(services.values()) else "degraded"
    return jsonify({"status":status,"services":services})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
