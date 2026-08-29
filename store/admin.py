from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Profile, SellerProfile, Cart, CartItem,
    ReelsVideo, ReelLike, ReelComment, Category, Brand,
    ChatMessage, Order, OrderItem, Product, ProductImage,
    Banner, Review, Wishlist, Coupon, OrderStatusHistory, PaymentTransaction
)

@admin.register(SellerProfile)
class SellerProfileAdmin(admin.ModelAdmin):
    list_display = ('store_name', 'user', 'phone', 'created_at')
    search_fields = ('store_name', 'user__username', 'phone')

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'phone')
    list_filter = ('role',)
    search_fields = ('user__username', 'phone')
    readonly_fields = ('user',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'link')
    list_filter = ('is_active',)
    search_fields = ('title',)

# Mahsulot rasmlari uchun inline
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'seller', 'category', 'price', 'stock', 'status', 'created_at')
    list_filter = ('status', 'category', 'brand', 'created_at')
    list_editable = ('price', 'stock', 'status')
    search_fields = ('name', 'description', 'seller__store_name')
    inlines = [ProductImageInline]

@admin.register(ReelsVideo)
class ReelsVideoAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'user', 'is_approved', 'views_count', 'created_at')
    list_filter = ('is_approved', 'created_at')
    list_editable = ('is_approved',)
    search_fields = ('title', 'description', 'user__username')
    readonly_fields = ('views_count', 'created_at', 'video_preview')
    
    fieldsets = (
        ('Asosiy Ma\'lumotlar', {
            'fields': ('user', 'title', 'description', 'price' )
        }),
        ('Media Fayllar', {
            'fields': ('video', 'video_preview', 'thumbnail')
        }),
        ('Holat va Statistikalar', {
            'fields': ('is_approved', 'views_count', 'created_at')
        }),
    )

    def video_preview(self, obj):
        if hasattr(obj, 'video') and obj.video:
            return format_html('<video src="{}" style="width: 150px; height: auto;" controls></video>', obj.video.url)
        return "Video yo'q"
    video_preview.short_description = "Video ko'rinishi"

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username',)

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'cart', 'product', 'quantity')
    search_fields = ('cart__user__username', 'product__name')

@admin.register(ReelLike)
class ReelLikeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'reel', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'reel__title')

@admin.register(ReelComment)
class ReelCommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'reel', 'text', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'reel__title', 'text')

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender', 'receiver', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('sender__username', 'receiver__username', 'message')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'customer_name', 'total_price', 'status', 'created_at')
    list_filter = ('status', 'created_at', 'payment_method')
    list_editable = ('status',)
    search_fields = ('user__username', 'customer_name', 'phone')

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'product', 'quantity', 'price')
    search_fields = ('order__id', 'product__name')

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product', 'created_at')
    search_fields = ('user__username', 'product__name')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('user__username', 'product__name', 'comment')

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_percent', 'active', 'valid_from', 'valid_to')
    list_filter = ('active', 'valid_from', 'valid_to')
    search_fields = ('code',)

@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('order__id', 'note')

@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'order', 'amount', 'provider', 'status', 'created_at')
    list_filter = ('provider', 'status', 'created_at')
    search_fields = ('transaction_id', 'order__id')