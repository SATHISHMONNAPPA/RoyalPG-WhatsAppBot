import os
import logging
from flask import Flask, request, jsonify
from werkzeug.middleware.proxy_fix import ProxyFix
from openai_service import OpenAIService
from twilio_service import TwilioService
from rate_limiter import RateLimiter
from config import SECRET_KEY, RATE_LIMIT_PER_MINUTE

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
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
    """
    Webhook endpoint to handle incoming WhatsApp messages from Twilio.
    """
    try:
        # Check if services are properly initialized
        if not all([openai_service, twilio_service, rate_limiter]):
            logger.error("Services not properly initialized")
            return jsonify({"error": "Service unavailable"}), 500
        
        # Get message data from Twilio
        incoming_msg = request.form.get('Body', '').strip()
        from_number = request.form.get('From', '')
        to_number = request.form.get('To', '')
        
        logger.info(f"Received message from {from_number}: {incoming_msg}")
        
        # Validate required fields
        if not incoming_msg or not from_number:
            logger.warning("Missing required fields in webhook request")
            return jsonify({"error": "Missing required fields"}), 400
        
        # Extract phone number without whatsapp: prefix for rate limiting
        phone_number = from_number.replace('whatsapp:', '')
        
        # Check rate limiting
        if rate_limiter and not rate_limiter.is_allowed(phone_number):
            logger.warning(f"Rate limit exceeded for {phone_number}")
            if twilio_service:
                twilio_service.send_rate_limit_message(from_number)
            return jsonify({"status": "rate_limited"}), 200
        
        # Handle empty or very short messages
        if len(incoming_msg.strip()) < 2:
            welcome_msg = ("Hello! 👋 Welcome to Royal PG. I'm here to help you with information about our "
                          "accommodation facilities near Oxford and Dayananda Sagar Engineering Colleges. "
                          "Feel free to ask about rooms, pricing, facilities, or location details!")
            if twilio_service:
                twilio_service.send_message(from_number, welcome_msg)
            return jsonify({"status": "welcome_sent"}), 200
        
        # Generate AI response
        try:
            if openai_service:
                ai_response = openai_service.generate_response(incoming_msg)
            else:
                ai_response = "I apologize, but the AI service is currently unavailable. Please contact Royal PG directly at +91-9876543210."
            
            # Send response back via WhatsApp
            success = False
            if twilio_service:
                success = twilio_service.send_message(from_number, ai_response)
            
            if success:
                logger.info(f"Response sent successfully to {from_number}")
                return jsonify({"status": "message_sent"}), 200
            else:
                logger.error(f"Failed to send response to {from_number}")
                return jsonify({"error": "Failed to send response"}), 500
                
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            # Send error message to user
            error_msg = ("I apologize for the technical difficulty. Please contact Royal PG directly at "
                        "+91-9876543210 for immediate assistance with your accommodation needs.")
            if twilio_service:
                twilio_service.send_message(from_number, error_msg)
            return jsonify({"error": "Processing failed"}), 500
    
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/test', methods=['POST'])
def test_message():
    """
    Test endpoint to simulate a WhatsApp message for development/testing.
    """
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({"error": "Message field required"}), 400
        
        test_message = data['message']
        phone_number = data.get('phone', 'test_user')
        
        logger.info(f"Test message: {test_message}")
        
        if openai_service:
            response = openai_service.generate_response(test_message)
            return jsonify({
                "user_message": test_message,
                "ai_response": response,
                "status": "success"
            })
        else:
            return jsonify({"error": "OpenAI service not available"}), 500
            
    except Exception as e:
        logger.error(f"Test endpoint error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/status')
def status():
    """Status endpoint to check service health."""
    service_status = {
        "openai_service": openai_service is not None,
        "twilio_service": twilio_service is not None,
        "rate_limiter": rate_limiter is not None
    }
    
    all_services_up = all(service_status.values())
    
    return jsonify({
        "status": "healthy" if all_services_up else "degraded",
        "services": service_status,
        "rate_limit_per_minute": RATE_LIMIT_PER_MINUTE
    }), 200 if all_services_up else 503

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    logger.info("Starting Royal PG WhatsApp Bot server...")
    app.run(host='0.0.0.0', port=5000, debug=True)
# Health check route for Render deployment
@app.route('/status', methods=['GET'])
def status():
    return jsonify({
        "status": "healthy",
        "services": {
            "twilio_service": services.get("twilio_service") is not None,
            "openai_service": services.get("openai_service") is not None,
            "rate_limiter": services.get("rate_limiter") is not None
        },
        "rate_limit_per_minute": config.get("rate_limit_per_minute", 10)
    }), 200

# Start the Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
