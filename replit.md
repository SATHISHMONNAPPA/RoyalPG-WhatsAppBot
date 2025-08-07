# Overview

Royal PG WhatsApp Bot is a customer service chatbot designed to handle inquiries about Royal PG, a premium accommodation facility in Bangalore for students and working professionals. The bot integrates with Twilio for WhatsApp messaging and OpenAI for intelligent response generation, providing automated customer support for room bookings, facility information, and general inquiries about the accommodation.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Web Framework
- **Flask-based REST API** with a single webhook endpoint (`/webhook`) to handle incoming WhatsApp messages from Twilio
- Uses `ProxyFix` middleware for proper handling behind reverse proxies
- Centralized configuration management through environment variables loaded via `python-dotenv`

## Service Layer Architecture
The application follows a modular service-oriented architecture with three core services:

### OpenAI Integration Service
- **Purpose**: Generates intelligent responses to customer inquiries using GPT models
- **Implementation**: Wraps OpenAI API calls with a specialized system prompt containing Royal PG facility information
- **Context Management**: Supports conversation history to maintain context across multiple message exchanges
- **Fallback Handling**: Graceful error handling with fallback responses when API calls fail

### Twilio WhatsApp Service  
- **Purpose**: Handles WhatsApp message sending and receiving via Twilio's API
- **Message Processing**: Automatically formats phone numbers with `whatsapp:` prefix for proper routing
- **Error Handling**: Comprehensive exception handling for Twilio API errors with detailed logging

### Rate Limiting Service
- **Purpose**: Prevents abuse by limiting requests per phone number to configurable limits (default: 10 per minute)
- **Implementation**: Time-window based rate limiting using in-memory storage with automatic cleanup of expired entries
- **User Experience**: Provides remaining request counts and sends notification messages when limits are exceeded

## Configuration Management
- **Environment-based Configuration**: All sensitive data (API keys, tokens) and operational parameters stored in environment variables
- **Business Logic Configuration**: Royal PG facility information, pricing, and contact details embedded in configuration for easy updates
- **Fallback Values**: Sensible defaults provided for non-critical configuration options

## Error Handling Strategy
- **Service Initialization**: Application continues running even if individual services fail to initialize, with graceful degradation
- **Request Processing**: Comprehensive error handling at each service layer with detailed logging for debugging
- **User Communication**: User-friendly error messages sent via WhatsApp when services are unavailable

# External Dependencies

## Third-party APIs
- **OpenAI GPT API**: For generating intelligent, contextual responses to customer inquiries about Royal PG facilities
- **Twilio WhatsApp API**: For sending and receiving WhatsApp messages, handling webhook notifications from Twilio's messaging service

## Development Dependencies  
- **Flask**: Web framework for handling HTTP requests and webhook endpoints
- **python-dotenv**: Environment variable management for configuration loading
- **Werkzeug**: WSGI utilities, specifically ProxyFix middleware for deployment behind reverse proxies

## Infrastructure Requirements
- **Environment Variables**: Requires OPENAI_API_KEY, TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, and TWILIO_PHONE_NUMBER
- **Webhook Endpoint**: Needs publicly accessible URL for Twilio to send webhook notifications
- **Runtime Environment**: Python 3.7+ with pip package management