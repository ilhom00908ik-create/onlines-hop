from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.utils.safestring import mark_safe

# Profil Modeli
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=50, choices=[('customer', 'Customer'), ('seller', 'Seller')], default='customer')
    phone = models.CharField(max_length=20, blank=True, null=True)
    avatar = models.ImageField(upload_to='profiles/avatars/', blank=True, null=True, verbose_name="Profil rasmi")
    bio = models.TextField(blank=True, null=True, verbose_name="O'zi haqida ma'lumot")

    def __str__(self):
        return self.user.username


class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Brand(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Banner(models.Model):
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='banners/')
    link = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title


# Sotuvchi Profili Modeli
class SellerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='seller_profile')
    store_name = models.CharField(max_length=255, verbose_name="Do'kon nomi")
    description = models.TextField(blank=True, null=True, verbose_name="Do'kon haqida")
    logo = models.ImageField(upload_to='sellers/logos/', blank=True, null=True, verbose_name="Logo")
    phone = models.CharField(max_length=20, verbose_name="Telefon")
    address = models.CharField(max_length=255, blank=True, null=True, verbose_name="Manzil")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.store_name


# Mahsulot Modeli
class Product(models.Model):
    seller = models.ForeignKey(SellerProfile, on_delete=models.SET_NULL, related_name='products', null=True, blank=True, verbose_name="Sotuvchi")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=255, verbose_name="Mahsulot nomi")
    price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Narxi")
    stock = models.IntegerField(default=0, verbose_name="Zaxira")
    status = models.BooleanField(default=True, verbose_name="Aktivlik")
    
    description = models.TextField(blank=True, null=True, verbose_name="To'liq ta'rifi va tuzilishi")
    specifications = models.JSONField(default=dict, blank=True, null=True, verbose_name="Xususiyatlari")
    
    image = models.ImageField(upload_to='products/main/', verbose_name="Asosiy rasm")
    video = models.FileField(upload_to='products/videos/', blank=True, null=True, verbose_name="Mahsulot videosi")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return self.name


# Qo'shimcha Rasmlar Modeli
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/gallery/', verbose_name="Qo'shimcha rasm")

    def __str__(self):
        return f"{self.product.name} - Rasm"


# Sevimli mahsulotlar (Wishlist)
class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlists', verbose_name="Foydalanuvchi")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='wishlisted_by', verbose_name="Mahsulot")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Qo'shilgan vaqti")

    class Meta:
        verbose_name = "Sevimli mahsulot"
        verbose_name_plural = "Sevimli mahsulotlar"
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"


# Sharhlar (Review)
class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews', verbose_name="Mahsulot")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews', verbose_name="Foydalanuvchi")
    rating = models.PositiveIntegerField(default=5, verbose_name="Reyting (1-5)")
    comment = models.TextField(verbose_name="Sharh matni")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Qo'shilgan vaqti")

    class Meta:
        verbose_name = "Sharh"
        verbose_name_plural = "Sharhlar"
        unique_together = ('product', 'user')

    def __str__(self):
        return f"{self.user.username} - {self.product.name} ({self.rating} yulduz)"


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)


class ReelsVideo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Foydalanuvchi")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, related_name='reels', verbose_name="Bog'langan mahsulot") # <--- MANA SHUNI QO'SHING
    title = models.CharField(max_length=255, verbose_name="Sarlavha")
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Narxi") # <--- MANA SHUNI QO'SHING
    description = models.TextField(blank=True, null=True, verbose_name="Tavsif")
    video = models.FileField(upload_to='reels/videos/', verbose_name="Video fayl")
    thumbnail = models.ImageField(upload_to='reels/thumbnails/', blank=True, null=True, verbose_name="Muqova (Thumbnail)")
    is_approved = models.BooleanField(default=False, verbose_name="Tasdiqlangan")
    views_count = models.PositiveIntegerField(default=0, verbose_name="Ko'rishlar soni")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Qo'shilgan vaqti")
   
    def __str__(self):
        return self.title

    def video_preview(self):
        if self.video:
            return mark_safe(f'<video width="300" controls><source src="{self.video.url}" type="video/mp4">Sizning brauzer video formatni qo\'llab-quvvatlamaydi.</video>')
        return "Video mavjud emas"
    video_preview.short_description = "Video Ko'rinishi"


class ReelLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reel = models.ForeignKey(ReelsVideo, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)


class ReelComment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reel = models.ForeignKey(ReelsVideo, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class ChatMessage(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    customer_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=50, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    payment_method = models.CharField(max_length=50, default='cash')


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=12, decimal_places=2)


class PaymentTransaction(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='transactions')
    transaction_id = models.CharField(max_length=255, unique=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    provider = models.CharField(max_length=50)
    status = models.CharField(max_length=50, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Transaction {self.transaction_id} - {self.status}"


class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True, verbose_name="Promokod")
    discount_percent = models.PositiveIntegerField(default=0, verbose_name="Chegirma foizi (%)")
    active = models.BooleanField(default=True, verbose_name="Faolligi")
    valid_from = models.DateTimeField(verbose_name="Boshlanish vaqti")
    valid_to = models.DateTimeField(verbose_name="Tugash vaqti")

    class Meta:
        verbose_name = "Promokod"
        verbose_name_plural = "Promokodlar"

    def __str__(self):
        return f"{self.code} ({self.discount_percent}%)"


class OrderStatusHistory(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Buyurtma qabul qilindi'),
        ('processing', 'Tayyorlanmoqda'),
        ('shipped', 'Yetkazib berishga chiqarildi'),
        ('delivered', 'Yetkazib berildi'),
        ('cancelled', 'Bekor qilindi'),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='status_history', verbose_name="Buyurtma")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, verbose_name="Status")
    note = models.TextField(blank=True, null=True, verbose_name="Izoh")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="O'zgartirilgan vaqti")

    class Meta:
        verbose_name = "Buyurtma tarixi"
        verbose_name_plural = "Buyurtma tarixi"
        ordering = ['-created_at']

    def __str__(self):
        return f"Buyurtma #{self.order.id} - {self.get_status_display()}"

class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Foydalanuvchi")
    product = models.ForeignKey('Product', on_delete=models.CASCADE, verbose_name="Mahsulot")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Qo'shilgan vaqti")

class Meta:
        unique_together = ('user', 'product') # Bir mahsulotni ikki marta qo'shib bo'lmaydi

def __str__(self):
        return f"{self.user.username} - {self.product.title}"