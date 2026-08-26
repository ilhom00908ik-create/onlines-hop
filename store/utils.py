import requests
import logging
from google import genai
from django.conf import settings

logger = logging.getLogger(__name__)

# Kalitlarni settings.py faylidan olish
TELEGRAM_BOT_TOKEN = getattr(settings, 'TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_ID = getattr(settings, 'TELEGRAM_CHAT_ID', '')


def _local_shop_assistant(message):
    """Gemini API key ulanmagan bo'lsa, do'kon bazasi asosida javob beradigan
    mahalliy yordamchi (AI yordamchi hech qachon 'javob bermaydi' holatda qolmaydi)"""
    from .models import Product

    text = (message or '').lower()
    products = Product.objects.filter(status='approved')[:5]

    # Mahsulotlar / narxlar haqidagi savollar
    product_keywords = ('mahsulot', 'narx', 'qancha', 'nima bor', 'katalog',
                        'tovar', 'product', 'price', 'telefon')
    if any(k in text for k in product_keywords):
        lines = ["🛍️ Do'konimizdagi mashhur mahsulotlar:"]
        for p in products:
            lines.append(f"• {p.name} — {p.price} so'm (omborda {p.stock} dona)")
        lines.append("")
        lines.append("Bosh sahifada barcha mahsulotlarni ko'rish va savatga qo'shish mumkin.")
        return chr(10).join(lines)

    # Buyurtma / yetkazib berish haqidagi savollar
    order_keywords = ('buyurtma', 'order', 'yetkazib', 'yetkazish', 'delivery',
                      'savat', 'cart', 'xarid')
    if any(k in text for k in order_keywords):
        steps = [
            "📦 Buyurtma berish tartibi:",
            "1. Bosh sahifadan kerakli mahsulotni tanlang",
            "2. «🛒 Savatga qo'shish» tugmasini bosing",
            "3. Yuqori menyudan «Savatcha» ga o'ting",
            "4. «Buyurtma berish» tugmasini bosib ism, telefon va manzil kiriting",
        ]
        return chr(10).join(steps)

    # Salomlashish
    greet_keywords = ('salom', 'assalomu', 'hello', 'hi ', 'hayrli', 'yordam')
    if any(k in text for k in greet_keywords):
        return ("Salom! 👋 Men do'kon yordamchisiman. "
                "Mahsulotlar, narxlar yoki buyurtma berish haqida so'rang.")

    # Boshqa savollar uchun umumiy javob
    parts = [
        "Men hozir cheklangan rejimda ishlayapman (Gemini API kaliti ulanmagan).",
        "",
        "Shu savollar bo'yicha yordam bera olaman:",
        "• «Nima mahsulotlar bor?» — narxlari bilan ro'yxati",
        "• «Buyurtma qanday beriladi?» — bosqichma-bosqich yo'riqnoma",
        "",
        "💡 To'liq AI javoblari uchun .env fayliga GEMINI_API_KEY ni qo'shing "
        "(kalitni https://aistudio.google.com/apikey dan oling).",
    ]
    return chr(10).join(parts)


def ask_gemini(prompt_text):
    """Gemini AI dan so'rov jo'natish"""
    api_key = getattr(settings, 'GEMINI_API_KEY', '')

    if not api_key:
        logger.warning("Gemini API key o'rnatilmagan — mahalliy yordamchi ishlatildi")
        return _local_shop_assistant(prompt_text)

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt_text,
        )
        logger.info(f"Gemini so'rovi muvaffaqiyatli: {prompt_text[:50]}...")
        return response.text
    except genai.APIError as e:
        logger.error(f"Gemini API xatosi: {str(e)}")
        return f"Gemini API xatosi: {str(e)}"
    except Exception as e:
        logger.error(f"Gemini so'rovida xatolik: {str(e)}")
        return f"Xatolik yuz berdi: {str(e)}"


def send_telegram_order_notification(order):
    """Telegram orqali buyurtma xabarnomasi yuborish"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logger.warning("Telegram konfiguratsiyasi to'liq emas")
        return False
    
    try:
        items_text = ""
        total_price = 0
        
        for item in order.items.all():
            item_total = item.quantity * item.product.price if item.product else 0
            total_price += item_total
            product_name = item.product.name if item.product else "O'chirilgan mahsulot"
            product_price = item.product.price if item.product else 0
            items_text += f"• {product_name} — {item.quantity} ta x ${product_price}\n"

        message = f"""
<b>🛒 Yangi Buyurtma!</b>

<b>👤 Xaridor:</b> {order.customer_name}
<b>📞 Tel:</b> {order.phone}
<b>📍 Manzil:</b> {order.address}

<b>📦 Mahsulotlar:</b>
{items_text}
<b>💰 Jami:</b> ${total_price}
<b>📅 Sana:</b> {order.created_at.strftime('%Y-%m-%d %H:%M')}
"""

        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "HTML"
        }
        
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            logger.info(f"Telegram xabarnomasi yuborildi (Order ID: {order.id})")
            return True
        else:
            logger.error(f"Telegram xatosi: {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        logger.error("Telegram API timeout")
        return False
    except requests.exceptions.RequestException as e:
        logger.error(f"Telegram so'rovida xatolik: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Buyurtma xabarnomasi yuborishda xatolik: {str(e)}")
        return False


def send_email_notification(user_email, subject, message):
    """Email xabarnomasi yuborish"""
    from django.core.mail import send_mail
    
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL or 'noreply@onlineshop.uz',
            [user_email],
            fail_silently=False,
        )
        logger.info(f"Email yuborildi: {user_email}")
        return True
    except Exception as e:
        logger.error(f"Email yuborishda xatolik: {str(e)}")
        return False


def calculate_order_total(order):
    """Buyurtma summasi hisoblash"""
    total = sum(
        item.quantity * item.price
        for item in order.items.all()
    )
    return total


def get_top_products(limit=5):
    """Eng mashhur mahsulotlarni olish"""
    from .models import Product
    try:
        return Product.objects.filter(
            status='approved'
        ).order_by('-created_at')[:limit]
    except Exception as e:
        logger.error(f"Top mahsulotlarni olishda xatolik: {str(e)}")
        return []


def get_user_cart_count(user):
    """Foydalanuvchining savat hajmini olish"""
    from .models import Cart
    try:
        cart = Cart.objects.get(user=user)
        return cart.items.count()
    except Cart.DoesNotExist:
        return 0
    except Exception as e:
        logger.error(f"Savat sonini olishda xatolik: {str(e)}")
        return 0