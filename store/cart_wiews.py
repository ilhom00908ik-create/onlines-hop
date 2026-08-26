from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Product, Cart, CartItem

# 1. Savatchani ko'rsatish
@login_required
def cart_detail(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)
    
    # Jami summani hisoblash
    total_price = sum(item.quantity * item.product.price for item in cart_items)

    context = {
        'cart': cart,
        'cart_items': cart_items,
        'total_price': total_price,
    }
    return render(request, 'cart.html', context)


# 2. AJAX orqali mahsulot sonini (+ / -) o'zgartirish
@login_required
def update_cart_quantity_ajax(request, item_id):
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
                    'total_price': total_price
                })

        cart = item.cart
        cart_items = CartItem.objects.filter(cart=cart)
        total_price = sum(i.quantity * i.product.price for i in cart_items)
        item_cost = item.quantity * item.product.price

        return JsonResponse({
            'status': 'ok',
            'quantity': item.quantity,
            'item_cost': item_cost,
            'total_price': total_price
        })

    return JsonResponse({'status': 'error'}, status=400)


# 3. Savatchaga mahsulot qo'shish
@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, _ = Cart.objects.get_or_create(user=request.user)
    
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect('cart_detail')


# 4. Savatchadan mahsulotni o'chirish
@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    return redirect('cart_detail')