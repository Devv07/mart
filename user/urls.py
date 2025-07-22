from django.urls import path
from . import views

app_name = 'user'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('products/', views.product_list, name='product_list'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('add-to-cart/<int:pk>/', views.add_to_cart, name='add_to_cart'),
    path('add-to-wishlist/<int:pk>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('remove-from-cart/<int:pk>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/', views.cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('buy-now/<int:pk>/', views.buy_now, name='buy_now'),
    path('payment-success/', views.payment_success, name='payment_success'),
    path('payment-failure/', views.payment_failure, name='payment_failure'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('delete-account/', views.delete_account, name='delete_account'),
]