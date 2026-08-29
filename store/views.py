import json
from decimal import Decimal, InvalidOperation

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.utils.http import url_has_allowed_host_and_scheme
from django.db.models import Q

from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import (
    Product, Cart, CartItem, ReelsVideo, ReelLike, ReelComment,
    Category, Brand, ChatMessage, Order, OrderItem, Profile
)
from .forms import (
    UserUpdateForm, ProfileUpdateForm, ProductForm, OrderForm, ReelsVideoForm
)
from .serializers import (
    ProductSerializer,
    CategorySerializer,
    BrandSerializer,
    BannerSerializer,
    ReviewSerializer,
    WishlistSerializer,
    OrderSerializer,
    CartSerializer,
    CartItemSerializer,
    ReelsVideoSerializer,
    ReelCommentSerializer,
    ReelLikeSerializer,
    ChatMessageSerializer,
    UserRegisterSerializer,
    ProfileSerializer,
    UserLoginSerializer,
    AuthTokenSerializer,
    ProductVariantSerializer,
    Review, CouponSerializer, Coupon,
    OrderStatusHistory,
    OrderStatusHistorySerializer
)
from .utils import ask_gemini, send_telegram_order_notification
from django.http import JsonResponse
from .models import Order, OrderItem, Product , Wishlist
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Product
from .telegram_bot import send_order_notification
from django.shortcuts import render, get_object_or_404
from .models import Product, SellerProfile
import qrcode
import io
import base64
from django.shortcuts import render, get_object_or_404
from .models import Order
from drf_spectacular.utils import extend_schema
# Views tepasiga ushbu importlarni to'g'rilang:
from drf_spectacular.utils import extend_schema
from .serializers import UserLoginSerializer
from .services import send_telegram_notification, generate_payment_qr
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .services import send_telegram_notification, generate_payment_qr
from django.conf import settings
import urllib.parse
from django.db.models import Min, Max

User = get_user_model()


# ===== MAHSULOT TAFSILOTLARI =====

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    reviews = product.reviews.all()
    
    if request.method == 'POST' and request.user.is_authenticated:
        rating = request.POST.get('rating', 5)
        comment = request.POST.get('comment')
        Review.objects.update_or_create(
            product=product, user=request.user,
            defaults={'rating': rating, 'comment': comment}
        )
        return redirect('product_detail', pk=pk)
        
    context = {
        'product': product,
        'reviews': reviews,
    }
    return render(request, 'store/product_detail.html', context)


# ===== SAHIFALAR =====
def home_view(request):
    query = request.GET.get('q', '')
    category_id = request.GET.get('category', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    
    products = Product.objects.all()

    # Qidiruv
    if query:
        products = products.filter(name__icontains=query)

    # Topilgan mahsulotlar ichidan eng arzon va eng qimmat narxni aniqlash
    price_range = products.aggregate(min_p=Min('price'), max_p=Max('price'))
    absolute_min = price_range['min_p'] or 0
    absolute_max = price_range['max_p'] or 0

    # Narx bo'yicha filtrni qo'llash
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)

    # Turkum bo'yicha filtr
    if category_id:
        products = products.filter(category_id=category_id)

    categories = Category.objects.all()
    brands = Brand.objects.all()  # <-- MUHIM: Brendlarni bazadan olib kelamiz

    context = {
        'products': products,
        'categories': categories,
        'brands': brands,           # <-- MUHIM: Shablonga uzatamiz
        'query': query,
        'selected_category': category_id,
        'absolute_min': absolute_min,
        'absolute_max': absolute_max,
        'min_price': min_price,
        'max_price': max_price,
        'total_products': products.count(),
    }
    return render(request, 'store/home.html', context)
def video_feed(request):
    """Reels orqali savdo qilish sahifasi"""
    # select_related('product') orqali mahsulot ma'lumotlarini tezkor yuklaymiz
    videos = ReelsVideo.objects.filter(is_approved=True).select_related('user', 'product')

    context = {
        'videos': videos,
    }
    return render(request, 'store/video_feed.html', context)
   

@login_required
def chat_view(request):
    """Chat sahifasi"""
    active_user = None
    messages_list = []

    sent_ids = set(ChatMessage.objects.filter(sender=request.user).values_list('receiver_id', flat=True))
    received_ids = set(ChatMessage.objects.filter(receiver=request.user).values_list('sender_id', flat=True))
    conversation_ids = sent_ids | received_ids

    conversations = User.objects.filter(id__in=conversation_ids)
    users = User.objects.exclude(id=request.user.id).exclude(id__in=conversation_ids)

    selected_user_id = request.GET.get('user_id')
    if selected_user_id:
        active_user = get_object_or_404(User, id=selected_user_id)
        messages_list = list(
            ChatMessage.objects.filter(
                (Q(sender=request.user, receiver=active_user) | Q(sender=active_user, receiver=request.user))
            ).order_by('created_at').select_related('sender', 'receiver')
        )
        ChatMessage.objects.filter(sender=active_user, receiver=request.user, is_read=False).update(is_read=True)

    if request.method == 'POST':
        receiver_id = request.POST.get('receiver_id')
        message_text = request.POST.get('message', '').strip()
        if receiver_id and message_text:
            receiver = get_object_or_404(User, id=receiver_id)
            ChatMessage.objects.create(sender=request.user, receiver=receiver, message=message_text)
            return redirect(f"{request.path}?user_id={receiver.id}")

    context = {
        'users': users,
        'conversations': conversations,
        'active_user': active_user,
        'messages_list': messages_list,
    }
    return render(request, 'store/chat.html', context)


def profile_view(request, username):
    # Foydalanuvchini topish
    user_profile = get_object_or_404(User, username=username)
    
    # Sevimli mahsulotlar
    wishlists = Wishlist.objects.filter(user=user_profile)
    
    # Oxirgi 5 ta xarid qilingan buyurtmalar va ularning status tarixi
    recent_orders = Order.objects.filter(user=user_profile).order_by('-created_at')[:5]
    
    context = {
        'user_profile': user_profile,
        'wishlists': wishlists,
        'recent_orders': recent_orders,
    }
    return render(request, 'store/profile.html', context)


@login_required
def edit_profile(request):
    """Profilni tahrirlash"""
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('profile', username=request.user.username)
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=profile)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    return render(request, 'store/edit_profile.html', context)


# ===== SAVATCHA LOGIKASI =====

@login_required
def cart_detail(request):
    """Savatcha sahifasi"""
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.select_related('product').all()
    
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
        'total_price': total_price,
    }
    return render(request, 'store/cart.html', context)


@login_required
def add_to_cart(request, product_id):
    """Savatga mahsulot qo'shish"""
    product = get_object_or_404(Product, id=product_id)
    cart, _ = Cart.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        try:
            quantity = int(request.POST.get('quantity', 1))
        except ValueError:
            quantity = 1

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )

        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        return redirect('cart_detail')

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': 1}
    )
    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect('cart_detail')


@login_required
@require_POST
def update_cart_quantity(request, item_id):
    """Savatdagi mahsulot miqdorini oshirish/kamaytirish (+ / -)"""
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    action = request.POST.get('action')  # 'increase' yoki 'decrease'
    
    if action == 'increase':
        cart_item.quantity += 1
        cart_item.save()
    elif action == 'decrease':
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()  # Miqdor 1 dan kamaysa, o'chiriladi
            
    return redirect('cart_detail')


@login_required
def update_cart(request, item_id, action):
    """Savatdagi mahsulot miqdorini URL orqali oshirish/kamaytirish"""
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    
    if action == 'increase':
        cart_item.quantity += 1
        cart_item.save()
    elif action == 'decrease':
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
            
    return redirect('cart_detail')


@login_required
def remove_from_cart(request, item_id):
    """Savatdan o'chirish"""
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    item.delete()
    messages.success(request, 'Mahsulot savatdan o\'chirildi.')
    return redirect('cart_detail')


@login_required
def checkout(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.select_related('product').all()
    
    if not cart_items.exists():
        messages.warning(request, "Savatingiz bo'sh!")
        return redirect('cart_detail')

    total_price = sum(item.product.price * item.quantity for item in cart_items)

    if request.method == 'POST':
        form = OrderForm(request.POST)
        payment_method = request.POST.get('payment_method', 'cash')

        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.payment_method = payment_method
            order.total_price = total_price
            first_name = form.cleaned_data.get('first_name', '')
            last_name = form.cleaned_data.get('last_name', '')
            order.customer_name = f"{first_name} {last_name}".strip()
            order.save()

            # Savatdagi har bir mahsulotni OrderItem ga o'tkazamiz
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    price=item.product.price,
                    quantity=item.quantity
                )

            # Telegram botga xabar yuborish
            try:
                send_order_notification(order)
            except Exception as e:
                print(f"Telegram notification error: {e}")

            # To'lov turiga qarab yo'naltirish (Click yoki Payme bo'lsa QR-kod sahifasiga)
            if payment_method in ['click', 'payme']:
                return redirect(f'/checkout/payment/{order.id}/?payment_method={payment_method}')

            # Naqd pulsiz bo'lsa savatni tozalaymiz va bosh sahifaga/muvaffaqiyatli sahifaga yo'naltiramiz
            cart.items.all().delete()
            messages.success(request, "Buyurtmangiz muvaffaqiyatli rasmiylashtirildi!")
            return redirect('order_success', order_id=order.id)
        else:
            # Validatsiyadan o'tmagan bo'lsa konsolga xatolikni chiqarish
            print("Form errors:", form.errors)
            messages.error(request, "Formani to'ldirishda xatolik bor. Iltimos, barcha maydonlarni tekshiring.")
    else:
        form = OrderForm()

    context = {
        'form': form,
        'cart': cart,
        'cart_items': cart_items,
        'total_price': total_price
    }
    return render(request, 'store/checkout.html', context)

@login_required
def order_success(request, order_id):
    """Buyurtma muvaffaqiyatli yakunlandi"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    context = {'order': order}
    return render(request, 'store/order_success.html', context)


# ===== SOTUVCHI VA AUTENTIFIKATSIYA =====

@login_required
def seller_dashboard(request):
    """Sotuvchi paneli"""
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    if profile.role != 'seller':
        return redirect('home')
    
    errors = []
    success_message = None
    
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        price_raw = request.POST.get('price', '').strip()
        stock_raw = request.POST.get('stock', '').strip()
        image = request.FILES.get('image')
        
        if not name:
            errors.append('Mahsulot nomi kiritilishi kerak.')
        if not description:
            errors.append('Mahsulot tavsifi kiritilishi kerak.')
        
        price = None
        try:
            price = Decimal(price_raw)
            if price <= 0:
                errors.append('Narx 0 dan katta bo\'lishi kerak.')
        except (InvalidOperation, TypeError):
            errors.append('Narx noto\'g\'ri kiritilgan.')
        
        stock = 0
        try:
            stock = int(stock_raw) if stock_raw else 0
            if stock < 0:
                errors.append('Ombor soni manfiy bo\'lishi mumkin emas.')
        except (ValueError, TypeError):
            errors.append('Ombor soni noto\'g\'ri kiritilgan.')
        
        if not image:
            errors.append('Mahsulot rasmi yuklanishi kerak.')
        
        if not errors:
            Product.objects.create(
                seller=request.user,
                name=name,
                description=description,
                price=price,
                stock=stock,
                image=image,
                status='pending',
            )
            success_message = 'Mahsulot qo\'shildi va moderatsiyaga yuborildi.'
            return redirect('seller_dashboard')
    
    products = Product.objects.filter(seller=request.user)
    pending_products = products.filter(status='pending')
    approved_products = products.filter(status='approved')
    
    context = {
        'products': products,
        'pending_products': pending_products,
        'approved_products': approved_products,
        'errors': errors,
        'success_message': success_message,
    }
    return render(request, 'store/seller_dashboard.html', context)


@login_required
@require_POST
def like_reel(request, reel_id):
    reel = get_object_or_404(ReelsVideo, id=reel_id)
    like, created = ReelLike.objects.get_or_create(user=request.user, reel=reel)
    if not created:
        like.delete()
    return redirect('video_feed')


@login_required
def add_reel_comment(request, reel_id):
    reel = get_object_or_404(ReelsVideo, id=reel_id)
    if request.method == 'POST':
        text = request.POST.get('text', '').strip()
        if text:
            ReelComment.objects.create(user=request.user, reel=reel, text=text)
    return redirect('video_feed')


def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')
        role = request.POST.get('role', 'customer')
        
        errors = []
        if not username:
            errors.append('Foydalanuvchi nomi kiritilishi kerak.')
        if User.objects.filter(username=username).exists():
            errors.append('Bu foydalanuvchi nomi allaqachon mavjud.')
        if not password1 or password1 != password2:
            errors.append('Parollar mos kelmadi yoki bo\'sh.')
        
        if not errors:
            user = User.objects.create_user(username=username, email=email, password=password1)
            Profile.objects.create(user=user, role=role)
            login(request, user)
            return redirect('home')
        
        context = {'errors': errors, 'username': username, 'email': email}
    else:
        context = {}
    
    return render(request, 'store/register.html', context)


def login_view(request):
    next_url = request.GET.get('next') or request.POST.get('next')
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
                return redirect(next_url)
            return redirect('home')
        else:
            context = {'error': "Noto'g'ri foydalanuvchi nomi yoki parol.", 'next': next_url or ''}
            return render(request, 'store/login.html', context)
    
    return render(request, 'store/login.html', {'next': next_url or ''})


@login_required
def logout_view(request):
    logout(request)
    return redirect('home')


# ===== AI CHATBOT =====

@require_POST
def ai_chat_api(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
        message = (data.get('message') or '').strip()
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({'bot_response': 'Noto\'g\'ri so\'rov formati.'}, status=400)
    
    if not message:
        return JsonResponse({'bot_response': 'Xabar bo\'sh bo\'lishi mumkin emas.'}, status=400)
    
    answer = ask_gemini(message)
    return JsonResponse({'bot_response': answer})


# ===== DRF API ENDPOINTS =====

class IsProductOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.seller == request.user or request.user.is_staff


class ProductListView(generics.ListCreateAPIView):
    queryset = Product.objects.all().order_by('-id')
    queryset = Product.objects.all()  # <--- Shu qatorni qo'shing
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        status_param = self.request.query_params.get('status', None)

        if status_param is not None:
            if str(status_param).lower() in ['approved', 'true', '1']:
                queryset = queryset.filter(status=True)
            elif str(status_param).lower() in ['pending', 'false', '0']:
                queryset = queryset.filter(status=False)

        return queryset

def get_queryset(self):
    queryset = Product.objects.all()
    status_param = self.request.query_params.get('status', None)
    
    if status_param is not None:
        # Agar status parametrimiz 'approved' bo'lsa True, 'pending' yoki boshqa bo'lsa False ga o'giramiz
        if str(status_param).lower() in ['approved', 'true', '1']:
            queryset = queryset.filter(status=True)
        elif str(status_param).lower() in ['pending', 'false', '0']:
            queryset = queryset.filter(status=False)
            
    return queryset
    
    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsProductOwnerOrReadOnly]


class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class BrandListView(generics.ListAPIView):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer


class ReelsVideoListView(generics.ListCreateAPIView):
    serializer_class = ReelsVideoSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        queryset = ReelsVideo.objects.select_related('user').prefetch_related('likes', 'comments')
        if self.request.user.is_authenticated:
            return queryset
        return queryset.filter(is_approved=True)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ReelCommentListView(generics.ListCreateAPIView):
    serializer_class = ReelCommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        reel_id = self.kwargs.get('reel_id')
        return ReelComment.objects.filter(reel_id=reel_id)
    
    def perform_create(self, serializer):
        reel_id = self.kwargs.get('reel_id')
        reel = get_object_or_404(ReelsVideo, id=reel_id)
        serializer.save(user=self.request.user, reel=reel)


class OrderListView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related('items')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


class ChatMessageListView(generics.ListCreateAPIView):
    serializer_class = ChatMessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return ChatMessage.objects.filter(receiver=self.request.user).select_related('sender', 'receiver')
    
    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register_api(request):
    serializer = UserRegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user_id': user.id,
            'username': user.username,
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_api(request):
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user_id': user.id,
                'username': user.username,
            }, status=status.HTTP_200_OK)
        
        return Response(
            {'detail': 'Noto\'g\'ri login yoki parol.'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def get_product_variants_api(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    variants = getattr(product, 'variants', None)
    if variants:
        data = list(variants.values())
        return Response(data, status=status.HTTP_200_OK)
    return Response([], status=status.HTTP_200_OK)

@login_required
def cart_update_ajax(request, item_id):
    if request.method == "POST":
        action = request.POST.get('action')
        item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        
        if action == 'increase':
            item.quantity += 1
            item.save()
        elif action == 'decrease':
            if item.quantity > 1:
                item.quantity -= 1
                item.save()
            else:
                item.delete()
                cart = Cart.objects.get(user=request.user)
                cart_items = CartItem.objects.filter(cart=cart)
                total_price = sum(i.quantity * i.product.price for i in cart_items)
                return JsonResponse({
                    'status': 'removed',
                    'item_id': item_id,
                    'total_price': f"{total_price:,}"
                })

        cart = item.cart
        cart_items = CartItem.objects.filter(cart=cart)
        total_price = sum(i.quantity * i.product.price for i in cart_items)
        
        # HTML template formati (X x PRICE so'm) uchun:
        item_cost_str = f"{item.quantity} x {item.product.price}"

        return JsonResponse({
            'status': 'ok',
            'quantity': item.quantity,
            'item_cost': item_cost_str,
            'total_price': f"{total_price:,}"
        })

    return JsonResponse({'status': 'error'}, status=400)
def create_order_view(request):
    # Seansdan emas, bazadan foydalanuvchi savatini olamiz
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.select_related('product').all()

    # Savatda mahsulot bor-yo'qligini tekshirish
    if not cart_items.exists():
        messages.warning(request, "Savatingiz bo'sh!")
        return redirect('cart_detail')

    total_price = sum(item.product.price * item.quantity for item in cart_items)

    if request.method == 'POST':
        customer_name = request.POST.get('customer_name', request.user.username)
        phone = request.POST.get('phone', '')
        address = request.POST.get('address', '')
        payment_method = request.POST.get('payment_method', 'cash')

        # 1. Buyurtma yaratamiz
        order = Order.objects.create(
            user=request.user,
            customer_name=customer_name,
            phone=phone,
            address=address,
            payment_method=payment_method,
            total_price=total_price,
            status='pending'
        )

        # 2. Savatdagi mahsulotlarni OrderItem ga saqlaymiz
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                price=item.product.price,
                quantity=item.quantity
            )

        # 3. Bazadagi savatni tozalaymiz
        cart.items.all().delete()

        # 4. Telegram bildirishnoma yuborish
        try:
            send_telegram_notification(order)
        except Exception as e:
            print(f"Telegram notification error: {e}")

        # 5. To'lov yoki muvaffaqiyat sahifasiga o'tkazish
        messages.success(request, "Buyurtmangiz qabul qilindi!")
        return redirect('payment_process', order_id=order.id)

    context = {
        'cart': cart,
        'cart_items': cart_items,
        'total_price': total_price
    }
    return render(request, 'store/checkout.html', context)
@login_required
def payment_process_view(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if request.method == 'POST':
        # Click yoki Payme to'lovi muvaffaqiyatli o'tdi deb hisoblaymiz
        order.status = 'paid'
        order.transaction_id = f"TEST_TXN_{order.id}_12345"
        order.save()
        return redirect('order_success', order_id=order.id)

    return render(request, 'store/payment.html', {'order': order})

@login_required
def order_success_view(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'store/order_success.html', {'order': order})

def send_telegram_notification(order):
    BOT_TOKEN = "381737778:AAGiVBEtSxQPXisuzX88O8fcLGdHYx5x1kk"
    CHAT_ID = "7389059494"  # Telegram ID si

# TO'G'RI KOD:
    message = f"🛒 Yangi buyurtma #{order.id}!\n\n" \
          f"👤 Mijoz: {order.first_name} {order.last_name}\n" \
          f"📞 Tel: {order.phone}\n" \
          f"📍 Manzil: {order.address}\n" \
          f"💳 To'lov usuli: {order.payment_method}\n" \
          f"💰 Summa: {order.total_price} so'm"  # total_amount EMAS, total_price bo'lishi kerak
    

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': CHAT_ID,
        'text': message,
        'parse_mode': 'HTML'
    }
    
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"Telegram notification error: {e}")

@login_required
def payment_process_view(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    # Click / Payme ilovalariga o'tish yoki QR generatsiya havolalari
    # Click deep link formati: https://my.click.uz/services/pay?service_id=YOUR_SERVICE_ID&merchant_id=YOUR_MERCHANT_ID&amount=PRICE&transaction_param=ORDER_ID
    click_merchant_id = getattr(settings, 'CLICK_MERCHANT_ID', '12345')
    click_service_id = getattr(settings, 'CLICK_SERVICE_ID', '67890')
    
    click_url = f"https://my.click.uz/services/pay?service_id={click_service_id}&merchant_id={click_merchant_id}&amount={order.total_price}&transaction_param={order.id}"
    
    # Payme link formati (Base64 kodlangan): m=MERCHANT_ID;ac.order_id=ORDER_ID;a=AMOUNT_IN_TIYIN
    payme_merchant_id = getattr(settings, 'PAYME_MERCHANT_ID', '12345')
    payme_url = f"https://checkout.paycom.uz/{payme_merchant_id}?amount={int(order.total_price * 100)}&account[order_id]={order.id}"

    # Standard QR generatsiya API (QuickChart / Google APIs orqali)
    if order.payment_method == 'payme':
        active_pay_url = payme_url
    else:
        active_pay_url = click_url

    qr_code_url = f"https://api.qrserver.com/v1/create-qr-code/?size=250x250&data={urllib.parse.quote(active_pay_url)}"

    if request.method == 'POST':
        # Mijoz "To'lov qildim" tugmasini bossa
        order.status = 'processing'
        order.save()
        
        # Adminga xabar yuborish
        send_telegram_notification(order)
        return redirect('order_success', order_id=order.id)

    context = {
        'order': order,
        'qr_code_url': qr_code_url,
        'pay_url': active_pay_url,
    }
    return render(request, 'store/payment.html', context)

@login_required
def checkout_view(request):
    cart = get_object_or_404(Cart, user=request.user)
    
    if not cart.items.exists():
        return redirect('cart_detail')

    if request.method == 'POST':
        customer_name = request.POST.get('customer_name')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        payment_method = request.POST.get('payment_method', 'cash')

        # 1. Buyurtmani bazada yaratish
        order = Order.objects.create(
            user=request.user,
            customer_name=customer_name,
            phone=phone,
            address=address,
            payment_method=payment_method,
            total_amount=cart.get_total_price(),
            status='pending'
        )

        # 2. Savatdagi mahsulotlarni OrderItem'ga o'tkazish
        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                price=item.product.price,
                quantity=item.quantity
            )

        # 3. Savatni tozalash
        cart.items.all().delete()

        # 4. Mantiqiy Yo'naltirish
        if payment_method == 'cash':
            # Naqd pul bo'lsa adminga darhol xabar ketadi va Success oynasiga o'tadi
            send_telegram_notification(order)
            return redirect('order_success', order_id=order.id)
        else:
            # Click yoki Payme bo'lsa QR-kodli to'lov sahifasiga o'tadi
            return redirect('payment_process', order_id=order.id)

    return render(request, 'store/checkout.html', {'cart': cart})

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    # Mahsulotning barcha rasmlarini olish
    gallery_images = product.images.all()
    
    # Omborda kam qolganlari boshida, ko'p qolganlari oxirida keladigan qilib 7-8 qator (taxminan 28-32 ta) mahsulotni olamiz
    related_products = Product.objects.exclude(pk=product.pk).order_by('stock')[:32]

    return render(request, 'store/product_detail.html', {
        'product': product,
        'gallery_images': gallery_images,
        'related_products': related_products
    })

def seller_profile(request, pk):
    seller = get_object_or_404(SellerProfile, pk=pk)
    products = seller.products.filter(is_active=True)
    return render(request, 'store/seller_profile.html', {
        'seller': seller,
        'products': products
    })

def order_payment_view(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    # Click & Payme Merchant sozlamalari (O'zingizning ID'laringizni qo'yasiz)
    CLICK_SERVICE_ID = "12345"
    CLICK_MERCHANT_ID = "67890"
    PAYME_MERCHANT_ID = "60b1234567890"

    # Summani tiyinda ko'rsatish (Payme tiyinda qabul qiladi: 1 so'm = 100 tiyin)
    amount_in_tiyin = int(order.total_price * 100)
    amount_in_som = int(order.total_price)

    # 1. Click Deep-Link va QR URL
    click_url = f"https://my.click.uz/services/pay?service_id={CLICK_SERVICE_ID}&merchant_id={CLICK_MERCHANT_ID}&amount={amount_in_som}&transaction_param={order.id}"
    
    # 2. Payme Deep-Link va QR URL (Base64 formatida params bilan)
    payme_raw = f"m={PAYME_MERCHANT_ID};ac.order_id={order.id};a={amount_in_tiyin}"
    payme_base64 = base64.b64encode(payme_raw.encode('utf-8')).decode('utf-8')
    payme_url = f"https://checkout.paycom.uz/{payme_base64}"

    # 3. QR Kodlarni Generatsiya qilish (Base64 rasm ko'rinishida)
    def generate_qr(url):
        qr = qrcode.QRCode(version=1, box_size=8, border=2)
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode('utf-8')

    click_qr = generate_qr(click_url)
    payme_qr = generate_qr(payme_url)

    context = {
        'order': order,
        'click_url': click_url,
        'payme_url': payme_url,
        'click_qr': click_qr,
        'payme_qr': payme_qr,
    }
    return render(request, 'store/order_payment.html', context)

def order_payment_view(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    CLICK_SERVICE_ID = "12345"
    CLICK_MERCHANT_ID = "67890"
    PAYME_MERCHANT_ID = "60b1234567890"

    amount_in_tiyin = int(order.total_price * 100)
    amount_in_som = int(order.total_price)

    # 1. Click & Payme havolalari
    click_url = f"https://my.click.uz/services/pay?service_id={CLICK_SERVICE_ID}&merchant_id={CLICK_MERCHANT_ID}&amount={amount_in_som}&transaction_param={order.id}"
    
    payme_raw = f"m={PAYME_MERCHANT_ID};ac.order_id={order.id};a={amount_in_tiyin}"
    payme_base64 = base64.b64encode(payme_raw.encode('utf-8')).decode('utf-8')
    payme_url = f"https://checkout.paycom.uz/{payme_base64}"

    # 2. Universal UzQR havolasi (Milliy QR standarti bo'yicha)
    # Ushbu havola barcha O'zbekiston bank va to'lov ilovalari tomonidan qo'llab-quvvatlanadi
    uzqr_url = f"https://qr.uzcard.uz/pay?merchant_id={CLICK_MERCHANT_ID}&amount={amount_in_som}&order_id={order.id}"

    # QR kod yaratuvchi yordamchi funksiya
    def generate_qr(url):
        qr = qrcode.QRCode(version=1, box_size=8, border=2)
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode('utf-8')

    context = {
        'order': order,
        'click_url': click_url,
        'payme_url': payme_url,
        'uzqr_url': uzqr_url,
        'click_qr': generate_qr(click_url),
        'payme_qr': generate_qr(payme_url),
        'uzqr_qr': generate_qr(uzqr_url),
    }
    return render(request, 'store/order_payment.html', context)
@extend_schema(request=UserLoginSerializer, responses={200: AuthTokenSerializer})
@api_view(['POST'])
def login_api(request):
    ...

@extend_schema(request=UserRegisterSerializer, responses={201: ProfileSerializer})
@api_view(['POST'])
def register_api(request):
    ...

@extend_schema(responses={200: ProductVariantSerializer(many=True)})
@api_view(['GET'])
def get_product_variants_api(request):
    ...
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def perform_create(self, serializer):
        # 1. Buyurtmani bazaga saqlaymiz
        order = serializer.save(user=self.request.user if self.request.user.is_authenticated else None)

        # 2. Telegram botga instant xabar yuboramiz
        try:
            send_telegram_notification(order)
        except Exception as e:
            print(f"Telegram funksiyasida xatolik: {e}")

        return order

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_validate(raise_exception=True)
        order = self.perform_create(serializer)
        
        headers = self.get_success_headers(serializer.data)
        response_data = serializer.data

        # 2. AGAR CLICK YOKI PAYME BO'LSA - QR KOD VA TO'LOV LINKINI QAYTARAMIZ:
        if order.payment_method in ['click', 'payme']:
            # Misol uchun Click to'lov havolasi (merchant_id va service_id larni o'zingizniki bilan almashtirasiz)
            if order.payment_method == 'click':
                payment_url = f"https://my.click.uz/services/pay?service_id=12345&merchant_id=67890&amount={order.total_price}&transaction_param={order.id}"
            else: # payme
                payment_url = f"https://checkout.paycom.uz/{base64_encoded_payme_params}"

            # Base64 ko'rinishidagi QR kod tasviri
            qr_code_base64 = generate_payment_qr(payment_url)

            response_data['payment_url'] = payment_url
            response_data['qr_code'] = qr_code_base64

        return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)
    def seller_profile(request, pk):
     return render(request, 'store/seller_profile.html', {'pk': pk})

def send_telegram_notification(order):
    try:
        # settings.py faylidagi O'ZGARUVCHI NOMLARI yozilishi kerak:
        token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
        chat_id = getattr(settings, 'TELEGRAM_CHAT_ID', None)

        if not token or not chat_id:
            print("Telegram token yoki chat_id topilmadi!")
            return

        message = (
            f"📦 <b>Yangi Buyurtma #{order.id}</b>\n\n"
            f"👤 <b>Mijoz:</b> {order.customer_name}\n"
            f"📞 <b>Tel:</b> {order.phone}\n"
            f"📍 <b>Manzil:</b> {order.address}\n"
            f"💳 <b>To'lov usuli:</b> {order.payment_method}\n"
            f"💰 <b>Summa:</b> {order.total_amount:,} so'm"
        )

        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "HTML"
        }
        
        response = requests.post(url, json=payload)
        print("TELEGRAM API RESP:", response.status_code, response.text)
        
    except Exception as e:
        print(f"Telegram notification error: {e}")

@login_required
def checkout_payment_view(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    payment_method = request.GET.get('payment_method', 'click') # click yoki payme

    # Click/Payme to'lov havolalarini shakllantirish (Merchant ID va parametrlar bilan)
    if payment_method == 'payme':
        # Payme implicit URL formati (so'm tiyinda ko'rsatiladi: * 100)
        amount_tiyin = int(order.total_price * 100)
        pay_url = f"https://checkout.paycom.uz/{base64.b64encode(f'm=YOUR_PAYME_MERCHANT_ID;ac.order_id={order.id};a={amount_tiyin}'.encode()).decode()}"
    else:
        # Click URL formati
        pay_url = f"https://my.click.uz/services/pay?service_id=YOUR_CLICK_SERVICE_ID&merchant_id=YOUR_CLICK_MERCHANT_ID&amount={order.total_price}&transaction_param={order.id}"

    # QR-kodni rasm ko'rinishida generatsiya qilish (Base64)
    qr_img = qrcode.make(pay_url)
    buffer = io.BytesIO()
    qr_img.save(buffer, format="PNG")
    qr_code_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

    context = {
        'order': order,
        'payment_method': payment_method,
        'pay_url': pay_url,
        'qr_code_base64': qr_code_base64,
    }
    return render(request, 'store/payment_checkout.html', context)


@login_required
def confirm_payment_complete(request, order_id):
    """To'lov tasdiqlanganda savatni tozalab bosh sahifaga qaytarish"""
    if request.method == "POST":
        order = get_object_or_404(Order, id=order_id, user=request.user)
        
        # Buyurtma holatini yangilash
        order.is_paid = True
        order.save()

        # Foydalanuvchi savatini tozalash
        Cart.objects.filter(user=request.user).delete()

        # Bosh sahifaga yo'naltirish
        return redirect('home')
        
    return redirect('home')


class WishlistViewSet(viewsets.ModelViewSet):
    serializer_class = WishlistSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class CouponViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Coupon.objects.filter(active=True)
    serializer_class = CouponSerializer
    permission_classes = [permissions.IsAuthenticated]

class OrderStatusHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = OrderStatusHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return OrderStatusHistory.objects.all()
        return OrderStatusHistory.objects.filter(order__user=user)

def toggle_wishlist(request, product_id):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'unauthorized'}, status=401)
    
    product = get_object_or_404(Product, id=product_id)
    wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, product=product)
    
    if not created:
        wishlist_item.delete()
        added = False
    else:
        added = True
        
    return JsonResponse({'success': True, 'added': added})