from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Tên danh mục")
    description = models.CharField(max_length=255, blank=True, null=True, verbose_name="Mô tả")

    class Meta:
        verbose_name = "Danh mục linh kiện"
        verbose_name_plural = "Các danh mục linh kiện"

    def __str__(self):
        return self.name

class Brand(models.Model):
    name = models.CharField(max_length=100, verbose_name="Tên thương hiệu")

    class Meta:
        verbose_name = "Thương hiệu"
        verbose_name_plural = "Các thương hiệu"

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name="Tên linh kiện")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products", verbose_name="Danh mục")
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name="products", verbose_name="Thương hiệu")
    price = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="Giá gốc (VNĐ)")
    discount_price = models.DecimalField(max_digits=12, decimal_places=0, blank=True, null=True, verbose_name="Giá khuyến mãi (VNĐ)")
    stock_quantity = models.PositiveIntegerField(default=0, verbose_name="Số lượng tồn kho")
    image = models.ImageField(upload_to="products/", blank=True, null=True, verbose_name="Ảnh tải lên")
    image_url = models.CharField(max_length=300, blank=True, null=True, verbose_name="Đường dẫn ảnh tĩnh/URL")
    specifications = models.TextField(blank=True, null=True, verbose_name="Thông số kỹ thuật")
    description = models.TextField(blank=True, null=True, verbose_name="Mô tả chi tiết")
    is_active = models.BooleanField(default=True, verbose_name="Đang kinh doanh")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")

    class Meta:
        verbose_name = "Linh kiện PC"
        verbose_name_plural = "Danh sách linh kiện PC"
        ordering = ['-id']

    def __str__(self):
        return self.name

    @property
    def final_price(self):
        return self.discount_price if self.discount_price and self.discount_price < self.price else self.price

    @property
    def discount_percent(self):
        if self.discount_price and self.discount_price < self.price:
            return round((1 - (self.discount_price / self.price)) * 100)
        return 0

    @property
    def get_image_url(self):
        if self.image:
            return self.image.url
        if self.image_url:
            return self.image_url
        return "/static/images/placeholder.svg"

class Order(models.Model):
    STATUS_CHOICES = [
        ('Chờ xử lý', 'Chờ xử lý'),
        ('Đang giao', 'Đang giao'),
        ('Đã hoàn thành', 'Đã hoàn thành'),
        ('Đã hủy', 'Đã hủy'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('COD', 'Thanh toán tiền mặt khi nhận hàng (COD)'),
        ('BANK_QR', 'Chuyển khoản VietQR (Quét mã QR ngân hàng)'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="orders", verbose_name="Tài khoản")
    customer_name = models.CharField(max_length=100, verbose_name="Tên người nhận")
    customer_phone = models.CharField(max_length=20, verbose_name="Số điện thoại")
    shipping_address = models.CharField(max_length=250, verbose_name="Địa chỉ giao hàng")
    order_date = models.DateTimeField(auto_now_add=True, verbose_name="Ngày đặt")
    total_amount = models.DecimalField(max_digits=14, decimal_places=0, verbose_name="Tổng tiền (VNĐ)")
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='COD', verbose_name="Phương thức thanh toán")
    is_paid = models.BooleanField(default=False, verbose_name="Đã thanh toán")
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Chờ xử lý', verbose_name="Trạng thái đơn")
    note = models.TextField(max_length=500, blank=True, null=True, verbose_name="Ghi chú giao hàng")

    class Meta:
        verbose_name = "Đơn đặt hàng"
        verbose_name_plural = "Danh sách đơn đặt hàng"
        ordering = ['-order_date']

    def __str__(self):
        return f"Đơn hàng #{self.id} - {self.customer_name}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items", verbose_name="Đơn hàng")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="order_items", verbose_name="Linh kiện")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Số lượng")
    unit_price = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="Đơn giá (VNĐ)")

    class Meta:
        verbose_name = "Chi tiết đơn hàng"
        verbose_name_plural = "Chi tiết các đơn hàng"

    def __str__(self):
        return f"{self.quantity}x {self.product.name}"

    @property
    def total_price(self):
        return self.quantity * self.unit_price
