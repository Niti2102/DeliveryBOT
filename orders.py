# orders.py

import pandas as pd

# Load the delivery data once
def load_orders():
    try:
        df = pd.read_csv("data/amazon_delivery.csv")

        # Create a dictionary with phone number as key
        orders = {}
        for _, row in df.iterrows():
            phone = str(row.get('phone_number', '')).strip()
            if not phone:
                continue
            orders[phone] = {
                "order_id": row.get("order_id", "N/A"),
                "status": row.get("status", "N/A"),
                "eta": row.get("eta", "N/A"),
                "address": row.get("address", "N/A")
            }
        return orders
    except Exception as e:
        print("Error loading orders:", e)
        return {}

# Search function by phone number
def get_order_by_phone(phone: str):
    orders = load_orders()
    return orders.get(phone.strip(), None)
