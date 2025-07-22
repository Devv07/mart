from django.urls import path
from . import views

app_name = 'vendor'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('products/create/', views.product_create, name='product_create'),  # Ensure this exists
    path('categories/create/', views.category_create, name='category_form'),
    path('manage-order/<int:order_id>/', views.manage_order, name='manage_order'),
]