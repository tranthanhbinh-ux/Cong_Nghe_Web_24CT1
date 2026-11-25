from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST
from decimal import Decimal
import urllib.parse

from .models import Category, Brand, Product, Order, OrderItem

def home(request):
    category_id = request.GET.get('category')
    search_query = request.GET.get('search')

    products = Product.objects.filter(is_active=True).select_related('category', 'brand')

    if category_id:
        products = products.filter(category_id=category_id)

    if search_query:
        products = products.filter(name__icontains=search_query)

    categories = Category.objects.all()
    brands = Brand.objects.all()

    context = {
        'products': products,
        'categories': categories,
        'brands': brands,
        'current_category': int(category_id) if category_id and category_id.isdigit() else None,
        'search_query': search_query or '',
    }
    return render(request, 'store/home.html', context)

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    related_products = Product.objects.filter(
        category=product.category,
        is_active=True
    ).exclude(id=product.id)[:4]

    context = {
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'store/product_detail.html', context)

# --- GIỎ HÀNG (SESSION BASED) ---

def cart_index(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total_amount = Decimal('0')

    for p_id, item_data in cart.items():
        subtotal = Decimal(str(item_data['unit_price'])) * item_data['quantity']
        total_amount += subtotal
        cart_items.append({
            'product_id': p_id,
            'name': item_data['name'],
            'category_name': item_data.get('category_name', 'Linh kiện'),
            'image_url': item_data.get('image_url', ''),
            'unit_price': Decimal(str(item_data['unit_price'])),
            'quantity': item_data['quantity'],
            'subtotal': subtotal,
        })

    context = {
        'cart_items': cart_items,
        'total_amount': total_amount,
    }
    return render(request, 'store/cart.html', context)

@require_POST
def add_to_cart_ajax(request):
    product_id = request.POST.get('productId')
    try:
        quantity = int(request.POST.get('quantity', 1))
    except (ValueError, TypeError):
        quantity = 1

    try:
        product = Product.objects.get(id=product_id, is_active=True)
    except Product.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Không tìm thấy sản phẩm!'}, status=404)

    cart = request.session.get('cart', {})
    p_key = str(product.id)

    unit_price = float(product.final_price)

    if p_key in cart:
        cart[p_key]['quantity'] += quantity
    else:
        cart[p_key] = {
            'name': product.name,
            'category_name': product.category.name if product.category else 'Linh kiện',
            'image_url': product.get_image_url,
            'unit_price': unit_price,
            'quantity': quantity,
        }

    request.session['cart'] = cart
    request.session.modified = True

    total_qty = sum(item['quantity'] for item in cart.values())

    return JsonResponse({
        'success': True,
        'message': f'Đã thêm {product.name} vào giỏ hàng!',
        'productName': product.name,
        'cartCount': total_qty,
    })

@require_POST
def update_cart_quantity(request):
    product_id = request.POST.get('productId')
    try:
        quantity = int(request.POST.get('quantity', 1))
    except (ValueError, TypeError):
        quantity = 1

    cart = request.session.get('cart', {})
    p_key = str(product_id)

    if p_key in cart:
        if quantity > 0:
            cart[p_key]['quantity'] = quantity
        else:
            del cart[p_key]
        request.session['cart'] = cart
        request.session.modified = True

    return redirect('cart_index')

def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    p_key = str(product_id)
    if p_key in cart:
        del cart[p_key]
        request.session['cart'] = cart
        request.session.modified = True
        messages.success(request, 'Đã xóa sản phẩm khỏi giỏ hàng.')
    return redirect('cart_index')

# --- ĐẶT HÀNG (CHECKOUT) ---

def checkout(request):
    cart = request.session.get('cart', {})
    if not cart:
        messages.error(request, 'Giỏ hàng của bạn đang trống!')
        return redirect('cart_index')

    cart_items = []
    total_amount = Decimal('0')

    for p_id, item_data in cart.items():
        subtotal = Decimal(str(item_data['unit_price'])) * item_data['quantity']
        total_amount += subtotal
        cart_items.append({
            'product_id': p_id,
            'name': item_data['name'],
            'unit_price': Decimal(str(item_data['unit_price'])),
            'quantity': item_data['quantity'],
            'subtotal': subtotal,
        })

    if request.method == 'POST':
        customer_name = request.POST.get('customer_name', '').strip()
        customer_phone = request.POST.get('customer_phone', '').strip()
        shipping_address = request.POST.get('shipping_address', '').strip()
        payment_method = request.POST.get('payment_method', 'COD').strip()
        note = request.POST.get('note', '').strip()

        if not customer_name or not customer_phone or not shipping_address:
            messages.error(request, 'Vui lòng điền đầy đủ tên, số điện thoại và địa chỉ nhận hàng!')
            return render(request, 'store/checkout.html', {'cart_items': cart_items, 'total_amount': total_amount})

        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            customer_name=customer_name,
            customer_phone=customer_phone,
            shipping_address=shipping_address,
            payment_method=payment_method,
            total_amount=total_amount,
            status='Chờ xử lý',
            note=note
        )

        for p_id, item_data in cart.items():
            try:
                prod = Product.objects.get(id=int(p_id))
                OrderItem.objects.create(
                    order=order,
                    product=prod,
                    quantity=item_data['quantity'],
                    unit_price=Decimal(str(item_data['unit_price']))
                )
                prod.stock_quantity = max(0, prod.stock_quantity - item_data['quantity'])
                prod.save()
            except Product.DoesNotExist:
                continue

        request.session['cart'] = {}
        request.session.modified = True

        return redirect('order_success', order_id=order.id)

    initial_name = ''
    initial_phone = ''
    initial_address = ''

    if request.user.is_authenticated:
        initial_name = request.user.get_full_name() or request.user.username
        initial_phone = getattr(request.user, 'profile', None) and request.user.profile.phone or ''

    context = {
        'cart_items': cart_items,
        'total_amount': total_amount,
        'initial_name': initial_name,
        'initial_phone': initial_phone,
        'initial_address': initial_address,
    }
    return render(request, 'store/checkout.html', context)

def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    vietqr_data = None
    if order.payment_method == 'BANK_QR':
        bank_id = "MB"            # Ngân hàng Quân Đội (MB Bank)
        bank_name = "Ngân hàng TMCP Quân Đội (MB Bank)"
        account_no = "0325511673" # Số tài khoản thụ hưởng
        account_name = "TRAN THANH BINH"
        memo = f"BUILDGEAR DH{order.id}"
        amount = int(order.total_amount)
        
        # Mã hóa tham số để tạo URL VietQR an toàn và chuẩn xác
        encoded_memo = urllib.parse.quote(memo)
        encoded_name = urllib.parse.quote(account_name)
        
        # Tạo URL VietQR chuẩn quốc gia (tự động điền số tiền và nội dung chuyển khoản)
        qr_url = f"https://img.vietqr.io/image/{bank_id}-{account_no}-compact2.png?amount={amount}&addInfo={encoded_memo}&accountName={encoded_name}"
        
        vietqr_data = {
            'bank_name': bank_name,
            'bank_id': bank_id,
            'account_no': account_no,
            'account_name': "TRẦN THANH BÌNH",
            'memo': memo,
            'amount': amount,
            'qr_url': qr_url,
        }

    return render(request, 'store/order_success.html', {
        'order': order,
        'vietqr': vietqr_data
    })

# --- TÀI KHOẢN (AUTH & PROFILE) ---

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Đăng nhập thành công! Chào mừng {user.get_full_name() or user.username}.')
            next_url = request.GET.get('next')
            return redirect(next_url or 'home')
        else:
            messages.error(request, 'Tên đăng nhập hoặc mật khẩu không chính xác!')

    return render(request, 'store/login.html')

def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        fullname = request.POST.get('fullname', '').strip()
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        if not username or not password:
            messages.error(request, 'Vui lòng nhập tên đăng nhập và mật khẩu!')
        elif password != confirm_password:
            messages.error(request, 'Mật khẩu xác nhận không khớp!')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Tên đăng nhập đã tồn tại, vui lòng chọn tên khác!')
        else:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=fullname
            )
            messages.success(request, 'Đăng ký tài khoản thành công! Vui lòng đăng nhập.')
            return redirect('login')

    return render(request, 'store/register.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'Đã đăng xuất thành công.')
    return redirect('home')

def my_orders(request):
    if not request.user.is_authenticated:
        messages.error(request, 'Vui lòng đăng nhập để xem đơn hàng của bạn!')
        return redirect('login')

    orders = Order.objects.filter(user=request.user).prefetch_related('items__product')
    return render(request, 'store/my_orders.html', {'orders': orders})

def profile(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == 'POST':
        fullname = request.POST.get('fullname', '').strip()
        email = request.POST.get('email', '').strip()
        new_password = request.POST.get('new_password', '')

        user = request.user
        user.first_name = fullname
        user.email = email
        if new_password:
            user.set_password(new_password)
        user.save()

        messages.success(request, 'Cập nhật thông tin cá nhân thành công!')
        return redirect('profile')

    return render(request, 'store/profile.html')
