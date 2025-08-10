Royal PG WhatsApp Bot - deploy notes.

1) Copy .env.example -> .env, fill values.
2) Test locally: python main.py (install requirements in a venv)
3) Deploy to Render / Railway / your host.
4) In Twilio Console > Sandbox for WhatsApp set "When a message comes in" to:
   https://<your-deployed-domain>/webhook (HTTP POST).
5) Join sandbox from your phone using the join code in Twilio Console.
6) Test with WhatsApp or use /test endpoint (POST JSON {"message":"hi"}).
