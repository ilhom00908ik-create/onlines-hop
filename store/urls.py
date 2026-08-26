from django.urls import path
from . import views

urlpatterns = [
    # 1. ASOSIY SAHIFALAR VA KATALOG
    path('', views.home_view, name='home'),
    path('home/', views.home_view, name='index'), 
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('seller/<int:pk>/', views.seller_profile, name='seller_profile'),
    
    # 2. SAVAT VA BUYURTMA
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/<str:action>/', views.update_cart, name='update_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('cart/update-ajax/<int:item_id>/', views.cart_update_ajax, name='cart_update_ajax'),
    path('order/success/<int:order_id>/', views.order_success, name='order_success'),
    
    # 3. REELS VA CHAT
    path('reels/', views.video_feed, name='video_feed'),
    path('reels/<int:reel_id>/like/', views.like_reel, name='like_reel'),
    path('reels/<int:reel_id>/comment/', views.add_reel_comment, name='add_reel_comment'),
    path('chat/', views.chat_view, name='chat'),
    path('chat/room/', views.chat_view, name='chat_view'),
    
    # 4. DASHBOARD VA PROFIL
    path('seller/dashboard/', views.seller_dashboard, name='seller_dashboard'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/<str:username>/', views.profile_view, name='profile'),
    
    # 5. AUTHENTICATION
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # 6. AI VA TO'LOVLAR ('ai_chat' va 'ai_chat_api' ikkala nom ham qo'shildi)
    path('api/ai-chat/', views.ai_chat_api, name='ai_chat'),
    path('api/ai-chat/v1/', views.ai_chat_api, name='ai_chat_api'),
    path('payment/<int:order_id>/', views.order_payment_view, name='order_payment'),
    path('checkout/payment/<int:order_id>/', views.checkout_payment_view, name='checkout_payment'),
    path('checkout/complete/<int:order_id>/', views.confirm_payment_complete, name='confirm_payment_complete'),

    
]