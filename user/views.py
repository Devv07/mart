from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.paginator import Paginator
from django.urls import reverse
from django.contrib import messages
import requests
import uuid
import hashlib
import base64
from vendor.models import Product, Order, Category
from .models import Cart, Wishlist
from core.models import CustomUser

@login_required
def dashboard(request):
    if request.user.role != 'user':
        return redirect('core:home')
    cart_items = Cart.objects.filter(user=request.user)
    products = Product.objects.filter(stock__gt=0)[:6]
    wishlist = Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True)
    cart_count = cart_items.count()
    return render(request, 'user/dashboard.html', {'cart_items': cart_items, 'products': products, 'wishlist': wishlist, 'cart_count': cart_count})

def product_list(request):
    query = request.GET.get('q', '')
    category_id = request.GET.get('category', '')
    products = Product.objects.filter(stock__gt=0).select_related('category')
    if query:
        products = products.filter(name__icontains=query)
    if category_id:
        products = products.filter(category_id=category_id)
    categories = Category.objects.all()
    paginator = Paginator(products, 9)
    page_number = request.GET.get('page')
    products_page = paginator.get_page(page_number)
    wishlist = Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True) if request.user.is_authenticated else []
    cart_count = Cart.objects.filter(user=request.user).count() if request.user.is_authenticated else 0
    return render(request, 'user/product_list.html', {
        'products': products_page,
        'categories': categories,
        'query': query,
        'category_id': category_id,
        'wishlist': wishlist,
        'cart_count': cart_count,
    })

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk, stock__gt=0)
    wishlist = Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True) if request.user.is_authenticated else []
    cart_count = Cart.objects.filter(user=request.user).count() if request.user.is_authenticated else 0
    return render(request, 'user/product_detail.html', {'product': product, 'wishlist': wishlist, 'cart_count': cart_count})

def add_to_wishlist(request, pk):
    if not request.user.is_authenticated:
        messages.info(request, 'Please log in to add items to your wishlist.')
        return redirect('core:login')
    if request.user.role != 'user':
        return redirect('core:home')
    product = get_object_or_404(Product, pk=pk, stock__gt=0)
    wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, product=product)
    if created:
        messages.success(request, f"{product.name} added to wishlist.")
    else:
        wishlist_item.delete()
        messages.success(request, f"{product.name} removed from wishlist.")
    return redirect(request.META.get('HTTP_REFERER', 'user:product_list'))

def add_to_cart(request, pk):
    if not request.user.is_authenticated:
        messages.info(request, 'Please log in to add items to your cart.')
        return redirect('core:login')
    if request.user.role != 'user':
        return redirect('core:home')
    product = get_object_or_404(Product, pk=pk, stock__gt=0)
    quantity = int(request.POST.get('quantity', 1))
    if quantity > product.stock:
        messages.error(request, f"Only {product.stock} items available.")
        return redirect(request.META.get('HTTP_REFERER', 'user:product_list'))
    cart_item, created = Cart.objects.get_or_create(user=request.user, product=product)
    if not created:
        cart_item.quantity += quantity
        cart_item.save()
    else:
        cart_item.quantity = quantity
        cart_item.save()
    messages.success(request, f"{product.name} added to cart.")
    return redirect('user:cart')

@login_required
def remove_from_cart(request, pk):
    if request.user.role != 'user':
        return redirect('core:home')
    cart_item = get_object_or_404(Cart, pk=pk, user=request.user)
    product_name = cart_item.product.name
    cart_item.delete()
    messages.success(request, f"{product_name} removed from cart.")
    return redirect('user:cart')

@login_required
def cart(request):
    if request.user.role != 'user':
        return redirect('core:home')
    cart_items = Cart.objects.filter(user=request.user).select_related('product')
    total = sum(item.product.price * item.quantity for item in cart_items)
    cart_count = cart_items.count()
    return render(request, 'user/cart.html', {'cart_items': cart_items, 'total': total, 'cart_count': cart_count})

@login_required
def checkout(request):
    if request.user.role != 'user':
        return redirect('core:home')
    cart_items = Cart.objects.filter(user=request.user).select_related('product')
    if not cart_items:
        messages.error(request, "Your cart is empty.")
        return redirect('user:cart')
    
    total = sum(item.product.price * item.quantity for item in cart_items)
    transaction_uuid = str(uuid.uuid4())
    order = Order.objects.create(
        user=request.user,
        product=cart_items[0].product,  # Handle multiple items in production
        quantity=sum(item.quantity for item in cart_items),
        total_amount=total,
        transaction_id=transaction_uuid
    )
    
    esewa_url = "https://uat.esewa.com.np/epay/main"
    esewa_params = {
        'amt': float(total),
        'pdc': 0,
        'psc': 0,
        'txAmt': 0,
        'tAmt': float(total),
        'pid': transaction_uuid,
        'scd': settings.ESEWA_MERCHANT_ID,
        'su': request.build_absolute_uri(reverse('user:payment_success')),
        'fu': request.build_absolute_uri(reverse('user:payment_failure')),
    }
    
    return render(request, 'user/checkout.html', {
        'cart_items': cart_items,
        'total': total,
        'esewa_url': esewa_url,
        'esewa_params': esewa_params,
        'cart_count': cart_items.count(),
    })

@login_required
def buy_now(request, pk):
    if request.user.role != 'user':
        return redirect('core:home')
    product = get_object_or_404(Product, pk=pk, stock__gt=0)
    quantity = int(request.POST.get('quantity', 1))
    if quantity > product.stock:
        messages.error(request, f"Only {product.stock} items available.")
        return redirect('user:product_detail', pk=pk)
    
    transaction_uuid = str(uuid.uuid4())
    order = Order.objects.create(
        user=request.user,
        product=product,
        quantity=quantity,
        total_amount=product.price * quantity,
        transaction_id=transaction_uuid
    )
    
    esewa_url = "https://uat.esewa.com.np/epay/main"
    esewa_params = {
        'amt': float(product.price * quantity),
        'pdc': 0,
        'psc': 0,
        'txAmt': 0,
        'tAmt': float(product.price * quantity),
        'pid': transaction_uuid,
        'scd': 'EPAYTEST',  # Replace with your eSewa merchant code
        'su': request.build_absolute_uri(reverse('user:payment_success')),
        'fu': request.build_absolute_uri(reverse('user:payment_failure')),
    }
    
    return render(request, 'user/checkout.html', {
        'cart_items': [{'product': product, 'quantity': quantity}],
        'total': product.price * quantity,
        'esewa_url': esewa_url,
        'esewa_params': esewa_params,
        'cart_count': Cart.objects.filter(user=request.user).count(),
    })

@login_required
def payment_success(request):
    if request.user.role != 'user':
        return redirect('core:home')
    pid = request.GET.get('pid')
    order = get_object_or_404(Order, transaction_id=pid, user=request.user)
    order.status = 'completed'
    order.save()
    # Clear cart for checkout
    if order.product:
        Cart.objects.filter(user=request.user, product=order.product).delete()
    else:
        Cart.objects.filter(user=request.user).delete()
    messages.success(request, "Payment successful. Order placed!")
    return redirect('user:dashboard')

@login_required
def payment_failure(request):
    if request.user.role != 'user':
        return redirect('core:home')
    pid = request.GET.get('pid')
    order = get_object_or_404(Order, transaction_id=pid, user=request.user)
    order.status = 'failed'
    order.save()
    messages.error(request, "Payment failed. Please try again.")
    return redirect('user:cart')

@login_required
def edit_profile(request):
    if request.user.role != 'user':
        return redirect('core:home')
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email').lower().strip()
        if CustomUser.objects.exclude(pk=request.user.pk).filter(email=email).exists():
            messages.error(request, 'Email is already in use.')
        else:
            request.user.username = username
            request.user.email = email
            request.user.save()
            messages.success(request, 'Profile updated successfully.')
        return redirect('user:dashboard')
    return render(request, 'user/edit_profile.html')

@login_required
def delete_account(request):
    if request.user.role != 'user':
        return redirect('core:home')
    if request.method == 'POST':
        user = request.user
        user.delete()
        messages.success(request, 'Your account has been deleted.')
        return redirect('core:home')
    return render(request, 'user/delete_account.html')

@login_required
def edit_order(request, order_id):
    if request.user.role != 'user':
        return redirect('core:home')
    order = Order.objects.get(id=order_id, user=request.user)
    if request.method == 'POST':
        status = request.POST.get('status')
        if status == 'cancelled' and order.status == 'pending':
            order.status = status
            order.save()
            messages.success(request, 'Order cancelled successfully.')
        else:
            messages.error(request, 'Cannot update order status.')
        return redirect('user:dashboard')
    return render(request, 'user/edit_order.html', {'order': order})

@login_required
def delete_order(request, order_id):
    if request.user.role != 'user':
        return redirect('core:home')
    order = Order.objects.get(id=order_id, user=request.user)
    if request.method == 'POST':
        if order.status == 'cancelled':
            order.delete()
            messages.success(request, 'Order deleted successfully.')
        else:
            messages.error(request, 'Only cancelled orders can be deleted.')
        return redirect('user:dashboard')
    return render(request, 'user/delete_order.html', {'order': order})