from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

from .models import (
    Profile, Category, Brand, Product, ProductImage, SellerProfile, 
    Cart, CartItem, Order, OrderItem
)


# ===== MODEL TESTS =====

class ProfileModelTest(TestCase):
    """Profile modeli testlari"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_profile_creation(self):
        """Profile yaratilishini tekshirish"""
        profile = Profile.objects.create(
            user=self.user,
            role='customer',
            phone='1234567890'
        )
        self.assertEqual(profile.user, self.user)
        self.assertEqual(profile.role, 'customer')

    def test_profile_str_method(self):
        """Profile __str__ metodini tekshirish"""
        profile = Profile.objects.create(
            user=self.user,
            role='seller'
        )
        self.assertEqual(str(profile), self.user.username)


class ProductModelTest(TestCase):
    """Product va ProductImage modeli testlari"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='seller',
            password='testpass123'
        )
        self.seller_profile = SellerProfile.objects.create(
            user=self.user,
            store_name='Test Store',
            phone='+998901234567'
        )
        self.category = Category.objects.create(
            name='Elektronika',
            slug='elektronika'
        )
        self.brand = Brand.objects.create(name='Samsung')

    def test_product_creation(self):
        """Mahsulot yaratilishini tekshirish"""
        product = Product.objects.create(
            seller=self.seller_profile,
            category=self.category,
            brand=self.brand,
            name='Telefon',
            description='Yangi telefon',
            specifications='RAM: 8GB\nROM: 128GB',
            price=500.00,
            stock=10,
            status=True
        )
        self.assertEqual(product.name, 'Telefon')
        self.assertEqual(product.seller, self.seller_profile)

    def test_product_str_method(self):
        """Product __str__ metodini tekshirish"""
        product = Product.objects.create(
            seller=self.seller_profile,
            category=self.category,
            name='Noutbuk',
            description='Yangi noutbuk',
            price=1000.00,
            status=False
        )
        self.assertEqual(product.name, 'Noutbuk')

    def test_product_image_gallery(self):
        """Mahsulot rasmlari (ProductImage) testi"""
        product = Product.objects.create(
            seller=self.seller_profile,
            category=self.category,
            name='Planshet',
            price=300.00,
            status=True
        )
        img = ProductImage.objects.create(product=product, image='products/test.jpg')
        self.assertEqual(product.images.count(), 1)


class OrderModelTest(TestCase):
    """Order modeli testlari"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='customer',
            password='testpass123'
        )

    def test_order_creation(self):
        """Buyurtma yaratilishini tekshirish"""
        order = Order.objects.create(
            user=self.user,
            customer_name='Ali Karim',
            phone='998901234567',
            address='Tashkent, Uzbekistan',
            total_price=100000,
            status='pending'
        )
        self.assertEqual(order.customer_name, 'Ali Karim')
        self.assertEqual(order.user, self.user)


# ===== VIEW TESTS =====

class HomeViewTest(TestCase):
    """Bosh sahifa testi"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.seller_profile = SellerProfile.objects.create(
            user=self.user,
            store_name='Home Store'
        )
        self.category = Category.objects.create(
            name='Test Category',
            slug='test-category'
        )
        self.product = Product.objects.create(
            seller=self.seller_profile,
            category=self.category,
            name='Test Product',
            description='Test',
            price=100.00,
            status=True
        )

    def test_home_view_status_code(self):
        """Bosh sahifa javob kodini tekshirish"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_home_view_template(self):
        """Bosh sahifa shablonini tekshirish"""
        response = self.client.get(reverse('home'))
        self.assertTemplateUsed(response, 'store/home.html')

    def test_home_view_contains_products(self):
        """Bosh sahifada mahsulotlar ko'rinishi"""
        response = self.client.get(reverse('home'))
        self.assertIn(self.product, response.context['products'])


class LoginViewTest(TestCase):
    """Kirish sahifasi testi"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

    def test_login_page_loads(self):
        """Login sahifasini tekshirish"""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

    def test_login_successful(self):
        """Muvaffaqiyatli login testi"""
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)


class PaymentViewTest(TestCase):
    """Click, Payme va UzQR to'lov sahifasi testi"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='buyer', password='testpass123')
        self.order = Order.objects.create(
            user=self.user,
            customer_name='Valibek',
            phone='998901112233',
            total_price=500000.00,
            status='pending'
        )

    def test_order_payment_view(self):
        """To'lov sahifasida QR-kodlar va integratsiyani tekshirish"""
        response = self.client.get(reverse('order_payment', args=[self.order.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'store/order_payment.html')
        self.assertIn('click_url', response.context)
        self.assertIn('payme_url', response.context)
        self.assertIn('uzqr_qr', response.context)


# ===== API TESTS =====

class ProductAPITest(APITestCase):
    """Mahsulot API testlari"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='seller',
            password='testpass123'
        )
        self.seller_profile = SellerProfile.objects.create(
            user=self.user,
            store_name='API Store'
        )
        self.category = Category.objects.create(
            name='Test Cat',
            slug='test-cat'
        )
        self.product = Product.objects.create(
            seller=self.seller_profile,
            category=self.category,
            name='API Test Product',
            description='Test',
            price=100.00,
            status=True
        )

    def test_product_list_api(self):
        """Mahsulotlar ro'yxati API testi"""
        response = self.client.get('/api/products/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_product_detail_api(self):
        """Mahsulot tafsilotlari API testi"""
        response = self.client.get(f'/api/products/{self.product.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class CartAPITest(APITestCase):
    """Savat API testlari"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='customer',
            password='testpass123'
        )
        Profile.objects.create(user=self.user, role='customer')
        self.cart = Cart.objects.create(user=self.user)

    def test_add_to_cart(self):
        """Savatga qo'shish testi"""
        self.client.force_authenticate(user=self.user)
        seller_user = User.objects.create_user(
            username='seller_cart',
            password='testpass123'
        )
        seller_profile = SellerProfile.objects.create(
            user=seller_user,
            store_name='Cart Store'
        )
        category = Category.objects.create(
            name='Test',
            slug='test'
        )
        product = Product.objects.create(
            seller=seller_profile,
            category=category,
            name='Test Product',
            description='Test',
            price=100.00,
            status=True
        )
        response = self.client.get(
            reverse('add_to_cart', args=[product.id])
        )
        self.assertEqual(response.status_code, 302)