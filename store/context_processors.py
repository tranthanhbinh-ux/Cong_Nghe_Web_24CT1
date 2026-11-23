def cart_count(request):
    """Context processor để trả về tổng số lượng sản phẩm trong giỏ hàng ra mọi template"""
    if hasattr(request, 'session'):
        cart = request.session.get('cart', {})
        total_qty = sum(item.get('quantity', 0) for item in cart.values())
        return {'cart_count': total_qty}
    return {'cart_count': 0}
