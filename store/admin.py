import json
from django.contrib import admin
from django.db.models import Sum, Count, Q
from django.utils.safestring import mark_safe
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.urls import reverse
from .models import Category, Brand, Product, Order, OrderItem

class RoleFilter(admin.SimpleListFilter):
    title = 'Vai trò tài khoản'
    parameter_name = 'role'

    def lookups(self, request, model_admin):
        return [
            ('admin', 'Quản trị viên (Admin)'),
            ('staff', 'Nhân viên (Staff)'),
            ('customer', 'Khách hàng (Customer)'),
        ]

    def queryset(self, request, queryset):
        if self.value() == 'admin':
            return queryset.filter(is_superuser=True)
        elif self.value() == 'staff':
            return queryset.filter(is_staff=True, is_superuser=False)
        elif self.value() == 'customer':
            return queryset.filter(is_staff=False, is_superuser=False)
        return queryset

try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass

@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    list_display = ('id', 'username', 'get_full_name', 'email', 'role_badge', 'is_active', 'date_joined')
    list_display_links = ('id', 'username')
    list_filter = (RoleFilter, 'is_active', 'date_joined')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('id',)

    def get_full_name(self, obj):
        name = f"{obj.first_name} {obj.last_name}".strip()
        return name if name else "Chưa đặt tên"
    get_full_name.short_description = "Họ và tên"

    def role_badge(self, obj):
        if obj.is_superuser:
            return mark_safe('<span class="badge badge-danger" style="font-size: 11px; padding: 5px 10px; background-color: #dc3545;"><i class="fas fa-crown mr-1"></i> Quản trị viên (Admin)</span>')
        elif obj.is_staff:
            return mark_safe('<span class="badge badge-warning text-dark font-weight-bold" style="font-size: 11px; padding: 5px 10px; background-color: #ffc107;"><i class="fas fa-user-tie mr-1"></i> Nhân viên (Staff)</span>')
        return mark_safe('<span class="badge badge-success" style="font-size: 11px; padding: 5px 10px; background-color: #198754;"><i class="fas fa-user mr-1"></i> Khách hàng (Customer)</span>')
    role_badge.short_description = "Vai trò (Role)"

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'product_count', 'description')
    search_fields = ('name',)

    def product_count(self, obj):
        count = obj.products.count()
        return mark_safe(f'<span class="badge badge-info" style="font-size: 11px; padding: 4px 8px;">{count} linh kiện</span>')
    product_count.short_description = "Số linh kiện"

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'product_count')
    search_fields = ('name',)

    def product_count(self, obj):
        count = obj.products.count()
        return mark_safe(f'<span class="badge badge-info" style="font-size: 11px; padding: 4px 8px;">{count} linh kiện</span>')
    product_count.short_description = "Số linh kiện"

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'image_tag',
        'name',
        'category_badge',
        'brand_badge',
        'price',
        'discount_price',
        'stock_quantity',
        'is_active',
        'actions_column'
    )
    list_display_links = ('name',)
    list_editable = ('price', 'discount_price', 'stock_quantity', 'is_active')
    list_filter = ('category', 'brand', 'is_active')
    search_fields = ('name', 'specifications')
    list_per_page = 20
    readonly_fields = ('image_preview', 'created_at')

    def image_tag(self, obj):
        url = obj.get_image_url
        edit_url = reverse('admin:store_product_change', args=[obj.id])
        return mark_safe(f'''
            <a href="{edit_url}" title="Nhấn để đổi ảnh / sửa linh kiện">
                <img src="{url}" style="width: 46px; height: 46px; object-fit: contain; border-radius: 6px; background: #0b1120; border: 1px solid #38bdf8; padding: 2px;" alt="{obj.name}" />
            </a>
        ''')
    image_tag.short_description = "Ảnh"

    def image_preview(self, obj):
        url = obj.get_image_url
        return mark_safe(f'<img src="{url}" style="max-width: 220px; max-height: 220px; object-fit: contain; border-radius: 8px; border: 1px solid #38bdf8; padding: 6px; background: #0b1120;" />')
    image_preview.short_description = "Xem trước ảnh"

    def category_badge(self, obj):
        return mark_safe(f'<span class="badge" style="background-color: #1e3a5f; color: #38bdf8; border: 1px solid #0284c7; font-size: 11px; padding: 5px 8px;">{obj.category.name}</span>')
    category_badge.short_description = "Danh mục"

    def brand_badge(self, obj):
        return mark_safe(f'<span class="badge" style="background-color: #334155; color: #f1f5f9; border: 1px solid #475569; font-size: 11px; padding: 5px 8px;">{obj.brand.name}</span>')
    brand_badge.short_description = "Thương hiệu"

    def actions_column(self, obj):
        edit_url = reverse('admin:store_product_change', args=[obj.id])
        view_url = reverse('product_detail', args=[obj.id])
        return mark_safe(f'''
            <div style="display: flex; gap: 6px; align-items: center; white-space: nowrap;">
                <a href="{edit_url}" class="btn btn-warning btn-sm" style="font-weight: 700; font-size: 11px; padding: 5px 12px; border-radius: 5px; color: #111; box-shadow: 0 2px 6px rgba(245, 158, 11, 0.4);" title="Chỉnh sửa tên, thay ảnh, thương hiệu, cấu hình chi tiết...">
                    <i class="fas fa-edit mr-1"></i> Sửa
                </a>
                <a href="{view_url}" target="_blank" class="btn btn-outline-info btn-sm" style="font-size: 11px; padding: 5px 10px; border-radius: 5px;" title="Xem sản phẩm ngoài website bán hàng">
                    <i class="fas fa-eye mr-1"></i> Xem
                </a>
            </div>
        ''')
    actions_column.short_description = "Thao tác"

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'quantity', 'unit_price', 'total_price')

    def total_price(self, instance):
        if instance and instance.pk and instance.unit_price and instance.quantity:
            return f"{instance.total_price:,.0f} đ".replace(',', '.')
        return "0 đ"
    total_price.short_description = "Thành tiền"

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_name', 'customer_phone', 'total_amount_display', 'payment_badge', 'is_paid', 'status_badge', 'order_date')
    list_filter = ('status', 'payment_method', 'is_paid', 'order_date')
    list_editable = ('is_paid',)
    search_fields = ('customer_name', 'customer_phone', 'shipping_address')
    inlines = [OrderItemInline]
    list_per_page = 20
    actions = ['mark_completed', 'mark_shipping', 'mark_paid', 'mark_cancelled']

    def total_amount_display(self, obj):
        val = f"{obj.total_amount:,.0f} đ".replace(',', '.')
        return mark_safe(f'<strong class="text-success">{val}</strong>')
    total_amount_display.short_description = "Tổng tiền"

    def payment_badge(self, obj):
        if obj.payment_method == 'BANK_QR':
            return mark_safe('<span class="badge badge-primary" style="font-size: 11px; padding: 5px 8px; background-color: #0d6efd;"><i class="fas fa-qrcode mr-1"></i> VietQR</span>')
        return mark_safe('<span class="badge badge-success" style="font-size: 11px; padding: 5px 8px; background-color: #198754;"><i class="fas fa-money-bill-wave mr-1"></i> Tiền mặt (COD)</span>')
    payment_badge.short_description = "Hình thức TT"

    def status_badge(self, obj):
        badge_styles = {
            'Chờ xử lý': 'badge-warning',
            'Đang giao': 'badge-info',
            'Đã hoàn thành': 'badge-success',
            'Đã hủy': 'badge-danger',
        }
        cls = badge_styles.get(obj.status, 'badge-secondary')
        return mark_safe(f'<span class="badge {cls}" style="font-size: 11px; padding: 5px 10px;">{obj.status}</span>')
    status_badge.short_description = "Trạng thái"

    @admin.action(description="Chuyển trạng thái sang: Đã hoàn thành")
    def mark_completed(self, request, queryset):
        rows = queryset.update(status='Đã hoàn thành')
        self.message_user(request, f"Đã cập nhật {rows} đơn hàng sang 'Đã hoàn thành'.")

    @admin.action(description="Chuyển trạng thái sang: Đang giao")
    def mark_shipping(self, request, queryset):
        rows = queryset.update(status='Đang giao')
        self.message_user(request, f"Đã cập nhật {rows} đơn hàng sang 'Đang giao'.")

    @admin.action(description="Đánh dấu: Đã nhận tiền thanh toán")
    def mark_paid(self, request, queryset):
        rows = queryset.update(is_paid=True)
        self.message_user(request, f"Đã cập nhật {rows} đơn hàng thành 'Đã nhận thanh toán'.")

    @admin.action(description="Chuyển trạng thái sang: Đã hủy")
    def mark_cancelled(self, request, queryset):
        rows = queryset.update(status='Đã hủy')
        self.message_user(request, f"Đã cập nhật {rows} đơn hàng sang 'Đã hủy'.")

# Admin headers
admin.site.site_header = "⚡ BuildGear PC Admin"
admin.site.site_title = "BuildGear Admin"
admin.site.index_title = "Bảng Điều Khiển Quản Lý"

# Custom Dashboard Index View
original_admin_index = admin.site.index

def custom_admin_index(request, extra_context=None):
    extra_context = extra_context or {}

    total_revenue = Order.objects.exclude(status='Đã hủy').aggregate(total=Sum('total_amount'))['total'] or 0
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status='Chờ xử lý').count()
    shipping_orders = Order.objects.filter(status='Đang giao').count()
    completed_orders = Order.objects.filter(status='Đã hoàn thành').count()
    cancelled_orders = Order.objects.filter(status='Đã hủy').count()

    total_products = Product.objects.count()
    low_stock_products = Product.objects.filter(stock_quantity__lte=5).count()
    total_customers = User.objects.filter(is_staff=False).count()

    recent_orders = Order.objects.order_by('-order_date')[:6]
    low_stock_items = Product.objects.filter(stock_quantity__lte=5).order_by('stock_quantity')[:6]

    # Category chart
    category_qs = Category.objects.annotate(prod_count=Count('products')).values('name', 'prod_count')
    category_labels = [c['name'].split(' - ')[0] for c in category_qs]
    category_counts = [c['prod_count'] for c in category_qs]

    # Order status chart
    order_status_labels = ['Chờ xử lý', 'Đang giao', 'Đã hoàn thành', 'Đã hủy']
    order_status_counts = [pending_orders, shipping_orders, completed_orders, cancelled_orders]

    extra_context.update({
        'total_revenue': total_revenue,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'shipping_orders': shipping_orders,
        'completed_orders': completed_orders,
        'cancelled_orders': cancelled_orders,
        'total_products': total_products,
        'low_stock_products': low_stock_products,
        'total_customers': total_customers,
        'recent_orders': recent_orders,
        'low_stock_items': low_stock_items,
        'category_labels_json': json.dumps(category_labels),
        'category_counts_json': json.dumps(category_counts),
        'order_status_labels_json': json.dumps(order_status_labels),
        'order_status_counts_json': json.dumps(order_status_counts),
    })
    return original_admin_index(request, extra_context=extra_context)

admin.site.index = custom_admin_index
