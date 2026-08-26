from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order
from .services import send_telegram_notification

@receiver(post_save, sender=Order)
def order_created_signal(sender, instance, created, **kwargs):
    if created:  # Faqat yangi buyurtma yaratilganda ishlaydi
        try:
            send_telegram_notification(instance)
        except Exception as e:
            print(f"Signal xatoligi: {e}")