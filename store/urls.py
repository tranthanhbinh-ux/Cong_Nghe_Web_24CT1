from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),

    # Cart
    path('cart/', views.cart_index, name='cart_index'),
    path('cart/add-ajax/', views.add_to_cart_ajax, name='add_to_cart_ajax'),
    path('cart/update/', views.update_cart_quantity, name='update_cart_quantity'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),

    # Checkout
    path('checkout/', views.checkout, name='checkout'),
    path('order-success/<int:order_id>/', views.order_success, name='order_success'),

    # Auth
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('my-orders/', views.my_orders, name='my_orders'),
]
