from fastapi import FastAPI, Request
from fastapi.responses import Response, PlainTextResponse
from twilio.twiml.voice_response import VoiceResponse
from orders import get_order_by_phone
from responder import generate_response
import pandas as pd

app = FastAPI()

# Session tracker for WhatsApp chatbot
user_sessions = {}

# Voice Call Handler
@app.post("/voice")
async def voice_handler(request: Request):
    form = await request.form()
    from_number = form.get("From", "").replace("whatsapp:", "").strip()

    # Step 1: Get order from phone number
    order = get_order_by_phone(from_number)

    # Step 2: Generate a nice response
    message = generate_response(order)

    # Step 3: Tell Twilio to speak it
    twilio_response = VoiceResponse()
    twilio_response.say(message)

    return Response(content=str(twilio_response), media_type="application/xml")


# WhatsApp Chatbot Handler
@app.post("/whatsapp")
async def whatsapp_handler(request: Request):
    form = await request.form()
    from_number = form.get("From", "").replace("whatsapp:", "").strip()
    body = form.get("Body", "").strip().lower()

    # Get current state of the user
    state = user_sessions.get(from_number, "start")

    if state == "start":
        user_sessions[from_number] = "awaiting_phone"
        reply = "👋 Hi there! Please enter your **phone number** to check your order status."
        return PlainTextResponse(f"<Response><Message>{reply}</Message></Response>", media_type="application/xml")

    elif state == "awaiting_phone":
        phone_input = body.replace(" ", "")
        df = pd.read_csv("data/orders.csv")


        # Try to find order
        order = df[df["phone_number"].str.replace(" ", "") == phone_input]

        if not order.empty:
            row = order.iloc[0]
            user_sessions[from_number] = "done"
            reply = (
                f"✅ Your order **{row['order_id']}** is **{row['order_status']}**, "
                f"and will arrive at **{row['location']}** by **{row['eta']}**."
            )
        else:
            reply = (
                "❌ Sorry, we couldn't find any order for that number. "
                "Please check and enter a valid phone number."
            )

        return PlainTextResponse(f"<Response><Message>{reply}</Message></Response>", media_type="application/xml")

    else:
        user_sessions[from_number] = "awaiting_phone"
        reply = "Please enter your phone number again to check your order status."
        return PlainTextResponse(f"<Response><Message>{reply}</Message></Response>", media_type="application/xml")
