from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Product, Order, Category
from .forms import ProductForm, CategoryForm
from django.core.paginator import Paginator


@login_required
def dashboard(request):
    if request.user.role != 'vendor':
        return redirect('core:home')
    products = Product.objects.filter(vendor=request.user)
    orders = Order.objects.filter(product__vendor=request.user)
    return render(request, 'vendor/dashboard.html', {'products': products, 'orders': orders})

@login_required
def manage_order(request, order_id):
    if request.user.role != 'vendor':
        return redirect('core:home')
    order = Order.objects.get(id=order_id, product__vendor=request.user)
    if request.method == 'POST':
        status = request.POST.get('status')
        if status in ['processing', 'shipped', 'cancelled'] and order.status == 'pending':
            order.status = status
            order.save()
            messages.success(request, f'Order {order.id} updated to {status}.')
        else:
            messages.error(request, 'Invalid status update.')
        return redirect('vendor:dashboard')
    return render(request, 'vendor/manage_order.html', {'order': order})

@login_required
def add_product(request):
    if request.user.role != 'vendor':
        return redirect('core:home')
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.vendor = request.user
            product.save()
            messages.success(request, f"{product.name} added successfully.")
            return redirect('vendor:dashboard')
        else:
            messages.error(request, 'Failed to add product. Please correct the errors.')
    else:
        form = ProductForm()
    return render(request, 'vendor/add_product.html', {'form': form})

@login_required
def add_category(request):
    if request.user.role != 'vendor':
        return redirect('core:home')
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save()
            messages.success(request, f"Category '{category.name}' added successfully.")
            return redirect('vendor:dashboard')
        else:
            messages.error(request, 'Failed to add category. Please correct the errors.')
    else:
        form = CategoryForm()
    return render(request, 'vendor/add_category.html', {'form': form})

@login_required
def product_create(request):
    if request.user.role != 'vendor':
        return redirect('/')
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.vendor = request.user
            product.status = 'approved'  # Set status to approved directly
            product.save()
            messages.success(request, 'Product created successfully!')
            return redirect('vendor:dashboard')
        else:
            messages.error(request, 'Error creating product. Please check the form.')
    else:
        form = ProductForm()
    return render(request, 'vendor/product_form.html', {'form': form})

@login_required
def product_update(request, pk):
    if request.user.role != 'vendor':
        return redirect('/')
    product = get_object_or_404(Product, pk=pk, vendor=request.user)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully!')
            return redirect('vendor:dashboard')
        else:
            messages.error(request, 'Error updating product. Please check the form.')
    else:
        form = ProductForm(instance=product)
    return render(request, 'vendor/product_form.html', {'form': form})

@login_required
def product_delete(request, pk):
    if request.user.role != 'vendor':
        return redirect('/')
    product = get_object_or_404(Product, pk=pk, vendor=request.user)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted successfully!')
        return redirect('vendor:dashboard')
    return render(request, 'vendor/product_confirm_delete.html', {'product': product})

@login_required
def orders(request):
    if request.user.role != 'vendor':
        return redirect('/')
    page = request.GET.get('page', 1)
    orders = Order.objects.filter(product__vendor=request.user)
    paginator = Paginator(orders, 10)
    orders_page = paginator.get_page(page)
    return render(request, 'vendor/orders.html', {'orders': orders_page})

@login_required
def category_create(request):
    if request.user.role != 'vendor':
        return redirect('/')
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category created successfully!')
            return redirect('vendor:dashboard')
        else:
            messages.error(request, 'Error creating category. Please check the form.')
    else:
        form = CategoryForm()
    return render(request, 'vendor/category_form.html', {'form': form})

@login_required
def category_update(request, pk):
    if request.user.role != 'vendor':
        return redirect('/')
    category = get_object_or_404(Category, pk=pk)
    if Product.objects.filter(category=category).exists():
        messages.error(request, 'Cannot edit category with associated products.')
        return redirect('vendor:dashboard')
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully!')
            return redirect('vendor:dashboard')
        else:
            messages.error(request, 'Error updating category. Please check the form.')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'vendor/category_form.html', {'form': form})

@login_required
def category_delete(request, pk):
    if request.user.role != 'vendor':
        return redirect('/')
    category = get_object_or_404(Category, pk=pk)
    if Product.objects.filter(category=category).exists():
        messages.error(request, 'Cannot delete category with associated products.')
        return redirect('vendor:dashboard')
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category deleted successfully!')
        return redirect('vendor:dashboard')
    return render(request, 'vendor/category_confirm_delete.html', {'category': category})