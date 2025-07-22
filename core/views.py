from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from vendor.models import Product, Category
from .forms import CustomUserCreationForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import CustomUser

def home(request):
    products = Product.objects.filter(stock__gt=0)[:6]
    categories = Category.objects.all()
    return render(request, 'home.html', {'products': products, 'categories': categories})

def login_view(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('/admin/')
        elif request.user.role == 'user':
            return redirect('user:dashboard')
        elif request.user.role == 'vendor':
            return redirect('vendor:dashboard')
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        print(f"POST data: email={email}, password=***")  # Debug
        if not email:
            print("Error: Email field is missing or empty")  # Debug
            messages.error(request, 'Email is required.')
            return render(request, 'login.html', {})
        email = email.lower().strip()
        print(f"Attempting to authenticate: email={email}")  # Debug
        try:
            user = CustomUser.objects.get(email=email)
            print(f"Found user: {user.email}, is_active: {user.is_active}, role: {user.role}, password_hash: {user.password}")  # Debug
        except CustomUser.DoesNotExist:
            print(f"User with email {email} does not exist")  # Debug
            messages.error(request, 'Invalid email or password.')
            return render(request, 'login.html', {})
        user = authenticate(request, email=email, password=password)
        if user is not None:
            print(f"Authenticated user: {user.email}, role: {user.role}, is_active: {user.is_active}")  # Debug
            if not user.is_active:
                messages.error(request, 'Your account is not active. Contact the admin.')
                return render(request, 'login.html', {})
            login(request, user)
            if user.is_staff:
                return redirect('/admin/')
            elif user.role == 'user':
                return redirect('user:dashboard')
            elif user.role == 'vendor':
                return redirect('vendor:dashboard')
        else:
            print("Authentication failed: Incorrect password or user not found")  # Debug
            messages.error(request, 'Invalid email or password.')
    return render(request, 'login.html', {})

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            print(f"Registered user: {user.email}, role: {user.role}, is_active: {user.is_active}, password_hash: {user.password}")  # Debug
            if user.role == 'vendor':
                user.is_active = False  # Vendors need admin verification
                user.save()
                messages.success(request, 'Registration successful. Awaiting admin verification.')
                return redirect('login')
            login(request, user)
            messages.success(request, 'Registration successful.')
            if user.role == 'user':
                return redirect('user:dashboard')
        else:
            print(f"Registration errors: {form.errors}")  # Debug
            messages.error(request, 'Registration failed. Please correct the errors.')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, 'Logged out successfully.')
    return redirect('core:login')  # Updated to use namespaced redirect

def check_session(request):
    return JsonResponse({'is_authenticated': request.user.is_authenticated})