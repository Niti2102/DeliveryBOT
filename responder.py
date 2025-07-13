# responder.py

def generate_response(order: dict) -> str:
    if not order:
        return (
            "Sorry, we couldn't find any order for this phone number. "
            "Please check and try again."
        )

    order_id = order.get("order_id", "unknown")
    status = order.get("status", "processing")
    eta = order.get("eta", "soon")
    address = order.get("address", "your address")

    response = (
        f"Hi! Your order **{order_id}** is currently **{status}**. "
        f"It's expected to reach you by **{eta}** at **{address}**. "
        "Let us know if you'd like to reschedule or leave any delivery instructions."
    )
    return response
