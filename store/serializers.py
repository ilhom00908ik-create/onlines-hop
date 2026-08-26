from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from django.contrib.auth import get_user_model
from .models import (
    Product, 
    Category, 
    Brand,
    Banner,
    Wishlist,
    Order, 
    OrderItem, 
    Cart, 
    CartItem, 
    ReelsVideo, 
    ReelComment, 
    ReelLike,
    ChatMessage
)

User = get_user_model()

# USER & AUTH SERIALIZERS
class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'first_name', 'last_name']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        return user


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id', 'username']


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class AuthTokenSerializer(serializers.Serializer):
    token = serializers.CharField()


# BRAND, CATEGORY, BANNER SERIALIZERS
class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = '__all__'


# PRODUCT SERIALIZERS
class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    brand = BrandSerializer(read_only=True)

    class Meta:
        model = Product
        fields = '__all__'


class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


class ReviewSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        fields = '__all__'


class WishlistSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = Wishlist
        fields = '__all__'


# CART SERIALIZERS
class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = CartItem
        fields = '__all__'


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = '__all__'


# ORDER SERIALIZERS
class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = '__all__'


# CHAT MESSAGE SERIALIZER
class ChatMessageSerializer(serializers.ModelSerializer):
    sender_username = serializers.CharField(source='sender.username', read_only=True)
    receiver_username = serializers.CharField(source='receiver.username', read_only=True)

    class Meta:
        model = ChatMessage
        fields = '__all__'


# REEL SERIALIZERS
class ReelLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReelLike
        fields = ['id', 'reel', 'user', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']


class ReelCommentSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = ReelComment
        fields = [
            'id', 
            'reel', 
            'user', 
            'user_username', 
            'text', 
            'created_at'
        ]
        read_only_fields = ['id', 'user', 'created_at']


class ReelsVideoSerializer(serializers.ModelSerializer):
    likes_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = ReelsVideo
        fields = [
            'id', 
            'title', 
            'video_file', 
            'product', 
            'created_at', 
            'likes_count', 
            'comments_count', 
            'is_liked'
        ]

    @extend_schema_field(serializers.IntegerField)
    def get_likes_count(self, obj):
        return obj.likes.count()

    @extend_schema_field(serializers.IntegerField)
    def get_comments_count(self, obj):
        return obj.comments.count()

    @extend_schema_field(serializers.BooleanField)
    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False