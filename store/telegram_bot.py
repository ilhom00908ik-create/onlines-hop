import os
import requests

def send_order_notification(order):
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_ADMIN_CHAT_ID')
    
    if not token or not chat_id:
        return

    text = f"🛍 **Yangi buyurtma!**\n\n" \
           f"🆔 **ID:** #{order.id}\n" \
           f"👤 **Xaridor:** {order.customer_name}\n" \
           f"📞 **Tel:** {order.phone}\n" \
           f"📍 **Manzil:** {order.address}\n" \
           f"💰 **Summa:** {order.total_price} so'm\n" \
           f"💳 **To'lov usuli:** {order.get_payment_method_display() if hasattr(order, 'get_payment_method_display') else order.payment_method}\n" \
           f"📌 **Holat:** {order.status}"

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    
    try:
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print(f"Telegram xabar yuborishda xatolik: {e}")