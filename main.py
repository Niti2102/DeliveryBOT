from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse, Response
from twilio.twiml.voice_response import VoiceResponse
import httpx

app = FastAPI()

# Track user sessions
user_sessions = {}

# Actual MockAPI orders endpoint
MOCKAPI_URL = "https://68734c03c75558e27353cdfa.mockapi.io/orders"

@app.post("/voice")
async def voice_handler(request: Request):
    form = await request.form()
    from_number = form.get("From", "").replace("whatsapp:", "").strip()

    twilio_response = VoiceResponse()
    twilio_response.say("Voice support not available yet. Please use WhatsApp.")
    return Response(content=str(twilio_response), media_type="application/xml")

@app.post("/whatsapp")
async def whatsapp_handler(request: Request):
    form = await request.form()
    from_number = form.get("From", "").replace("whatsapp:", "").strip()
    body = form.get("Body", "").strip().lower()

    state = user_sessions.get(from_number, "start")

    if state == "start":
        user_sessions[from_number] = "awaiting_phone"
        reply = "👋 Hi there! Please enter your **phone number** to check your order status."
        return PlainTextResponse(f"<Response><Message>{reply}</Message></Response>", media_type="application/xml")

    elif state == "awaiting_phone":
        phone_input = body.replace(" ", "").lower()

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(MOCKAPI_URL)
                orders = response.json()

            matched_order = next((order for order in orders if order.get("phone", "").replace(" ", "").lower() == phone_input), None)

            if matched_order:
                reply = (
                    f"✅ Your order **#{matched_order['id']}** is on the way!\n"
                    f"📦 ETA: **{matched_order['eta']}**\n"
                    f"📍 Address: **{matched_order['address']}**"
                )
                user_sessions[from_number] = "done"
            else:
                reply = (
                    "❌ Sorry, we couldn't find any order for that number.\n"
                    "Please make sure it's correct and try again."
                )

        except Exception as e:
            reply = f"⚠️ Oops! Something went wrong: {str(e)}"

        return PlainTextResponse(f"<Response><Message>{reply}</Message></Response>", media_type="application/xml")

    else:
        user_sessions[from_number] = "awaiting_phone"
        reply = "Please enter your phone number again to check your order status."
        return PlainTextResponse(f"<Response><Message>{reply}</Message></Response>", media_type="application/xml")
