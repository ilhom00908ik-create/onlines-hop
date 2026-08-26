from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from store.models import (
    Profile, Category, Brand, Product
)


class Command(BaseCommand):
    help = 'Sample ma\'lumotlarini baza ichiga qo\'shish'

    def handle(self, *args, **options):
        self.stdout.write("Sample ma'lumotlar qo'shilmoqda...")

        # Kategoriyalarni yaratish
        categories = [
            ('Elektronika', 'elektronika'),
            ('Kiyim va oyoq kiyim', 'kiyim'),
            ('Kitoblar', 'kitoblar'),
            ('Sport va dam olish', 'sport'),
            ('Uy-joy uchun', 'uy-joy'),
        ]
        
        created_categories = {}
        for name, slug in categories:
            cat, created = Category.objects.get_or_create(
                name=name,
                defaults={'slug': slug}
            )
            created_categories[name] = cat
            if created:
                self.stdout.write(f"✓ Kategoriya yaratildi: {name}")

        # Brendlarni yaratish
        brands_list = [
            'Samsung', 'Apple', 'Nokia', 'Sony', 'LG',
            'Adidas', 'Nike', 'Puma', 'Gucci', 'Zara'
        ]
        
        created_brands = {}
        for name in brands_list:
            brand, created = Brand.objects.get_or_create(name=name)
            created_brands[name] = brand
            if created:
                self.stdout.write(f"✓ Brend yaratildi: {name}")

        # Admin foydalanuvchisini tekshirish/yaratish
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@onlineshop.uz',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            Profile.objects.get_or_create(
                user=admin_user,
                defaults={'role': 'admin'}
            )
            self.stdout.write("✓ Admin foydalanuvchisi yaratildi")

        # Test sotuvchi yaratish
        seller, created = User.objects.get_or_create(
            username='seller1',
            defaults={'email': 'seller@onlineshop.uz'}
        )
        if created:
            seller.set_password('seller123')
            seller.save()
            Profile.objects.get_or_create(
                user=seller,
                defaults={'role': 'seller', 'phone': '+998901234567'}
            )
            self.stdout.write("✓ Test sotuvchi yaratildi")

        # Sample mahsulotlarni yaratish
        sample_products = [
            {
                'name': 'Samsung Galaxy S23',
                'description': 'Eng yangi Samsung telefoniki, super kamera va batareya',
                'price': 999.99,
                'stock': 50,
                'category': 'Elektronika',
                'brand': 'Samsung'
            },
            {
                'name': 'iPhone 15',
                'description': 'Apple\'ning eng kuchli telefoniki',
                'price': 1199.99,
                'stock': 30,
                'category': 'Elektronika',
                'brand': 'Apple'
            },
            {
                'name': 'Nike Air Max',
                'description': 'Zamonaviy va qulay oyoq kiyim',
                'price': 149.99,
                'stock': 100,
                'category': 'Kiyim va oyoq kiyim',
                'brand': 'Nike'
            },
            {
                'name': 'Adidas UltraBoost',
                'description': 'Professional sport oyoq kiyimi',
                'price': 189.99,
                'stock': 80,
                'category': 'Kiyim va oyoq kiyim',
                'brand': 'Adidas'
            },
            {
                'name': 'Sony Wireless Headphones',
                'description': 'Yuqori sifatli tovush bilan sutkazish',
                'price': 299.99,
                'stock': 40,
                'category': 'Elektronika',
                'brand': 'Sony'
            },
        ]

        for prod_data in sample_products:
            category = created_categories.get(prod_data['category'])
            brand = created_brands.get(prod_data['brand'])
            
            product, created = Product.objects.get_or_create(
                name=prod_data['name'],
                seller=seller,
                defaults={
                    'description': prod_data['description'],
                    'price': prod_data['price'],
                    'stock': prod_data['stock'],
                    'category': category,
                    'brand': brand,
                    'status': 'approved'
                }
            )
            if created:
                self.stdout.write(f"✓ Mahsulot yaratildi: {prod_data['name']}")

        self.stdout.write(self.style.SUCCESS('✅ Barcha sample ma\'lumotlar muvaffaqiyatli qo\'shildi!'))
        self.stdout.write("Admin login: admin / admin123")
        self.stdout.write("Seller login: seller1 / seller123")
