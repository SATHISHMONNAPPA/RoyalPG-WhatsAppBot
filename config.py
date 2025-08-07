import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# OpenAI Configuration
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# Twilio Configuration
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.environ.get("TWILIO_PHONE_NUMBER", "whatsapp:+14155238886")  # Default sandbox number

# Flask Configuration
SECRET_KEY = os.environ.get("SESSION_SECRET", "fallback-secret-key")

# Rate Limiting Configuration
RATE_LIMIT_PER_MINUTE = int(os.environ.get("RATE_LIMIT_PER_MINUTE", "10"))

# Royal PG Information - This will be part of the system prompt
ROYAL_PG_INFO = """
Royal PG is a premium accommodation facility located in Bangalore, specifically designed for students and working professionals.

ACCOMMODATION DETAILS:
- 2-sharing rooms: ₹8,500 per month
- 3-sharing rooms: ₹7,000 per month  
- 4-sharing rooms: ₹6,000 per month

FACILITIES INCLUDED:
- Unlimited meals (breakfast, lunch, dinner, and evening snacks)
- High-speed WiFi throughout the premises
- Laundry services
- 24/7 water supply
- Power backup
- Common areas for recreation
- Study rooms
- Parking facility
- Security with CCTV surveillance

LOCATION BENEFITS:
- Close proximity to Oxford Engineering College
- Near Dayananda Sagar Engineering College
- Good connectivity to major IT hubs
- Easy access to public transport

CONTACT INFORMATION:
- Address: Near Oxford & Dayananda Sagar Engineering Colleges, Bangalore
- Phone: +91-9876543210
- Email: info@royalpg.com

ADDITIONAL SERVICES:
- Room cleaning service
- Maintenance support
- Common kitchen access
- Recreation facilities
- Study environment

The PG maintains high standards of cleanliness, safety, and provides a comfortable living environment for students and professionals.
"""
