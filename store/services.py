import qrcode
import io
import base64
import requests
from django.conf import settings

def send_telegram_notification(order):
    bot_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', '8381737778:AAGiVBEtSxQPXisuzX88O8fcLGdHYx5x1kk')
    admin_chat_id = getattr(settings, 'TELEGRAM_ADMIN_CHAT_ID', '7389059494')

    items_text = ""
    if hasattr(order, 'items') and order.items.exists():
        for item in order.items.all():
            items_text += f"- {item.product.name} ({item.quantity} ta) - {item.price * item.quantity} so'm\n"
    else:
        items_text = "Mahsulotlar ro'yxati biriktirilmagan\n"

    payment_method_display = "Naqd pul 💵" if getattr(order, 'payment_method', '') == 'cash' else str(getattr(order, 'payment_method', '')).upper()
    payment_status_display = "To'langan ✅" if getattr(order, 'is_paid', False) else "Kutilmoqda ⏳"

    customer_name = getattr(order, 'customer_name', None) or (order.user.username if getattr(order, 'user', None) else 'Mehmon')
    phone = getattr(order, 'phone', 'Kiritilmagan')
    address = getattr(order, 'address', 'Kiritilmagan')
    total_price = getattr(order, 'total_price', 0)

    message = (
        f"🚨 **YANGI BUYURTMA #{order.id}** 🚨\n\n"
        f"👤 **Mijoz:** {customer_name}\n"
        f"📞 **Telefon:** {phone}\n"
        f"📍 **Manzil:** {address}\n"
        f"💳 **To'lov turi:** {payment_method_display}\n"
        f"📌 **Status:** {payment_status_display}\n"
        f"💰 **Jami summasi:** {total_price} so'm\n\n"
        f"📦 **Mahsulotlar:**\n{items_text}"
    )

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        'chat_id': admin_chat_id,
        'text': message,
        'parse_mode': 'Markdown'
    }
    
    try:
        response = requests.post(url, json=payload, timeout=5)
        print("TELEGRAM API RESP:", response.status_code, response.text)
    except Exception as e:
        print(f"Telegram yuborishda xatolik: {e}")


def generate_payment_qr(payment_url):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(payment_url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    return f"data:image/png;base64,{qr_base64}"