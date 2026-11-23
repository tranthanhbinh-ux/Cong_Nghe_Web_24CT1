import os
import sys
import shutil
import django

# Khởi tạo môi trường Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'buildgear.settings')
django.setup()

from django.contrib.auth.models import User
from store.models import Category, Brand, Product

def run_seed():
    print("🚀 Bắt đầu khởi tạo dữ liệu mẫu cho BuildGear...")

    # 1. Sao chép banner.png từ dự án cũ nếu có
    old_banner_path = r"C:\Users\Admin\source\repos\buildgear\buildgear\Content\images\banner.png"
    target_banner_path = os.path.join("store", "static", "images", "banner.png")
    os.makedirs(os.path.join("store", "static", "images"), exist_ok=True)
    if os.path.exists(old_banner_path) and not os.path.exists(target_banner_path):
        shutil.copy(old_banner_path, target_banner_path)
        print("✅ Đã sao chép banner.png vào store/static/images/")

    # 2. Tạo tài khoản mẫu
    # Admin: admin / 123456
    if not User.objects.filter(username="admin").exists():
        User.objects.create_superuser("admin", "admin@buildgear.vn", "123456", first_name="Quản Trị Viên")
        print("✅ Đã tạo Superuser Admin: admin / 123456")

    # Staff: staff / 123456
    if not User.objects.filter(username="staff").exists():
        from django.contrib.auth.models import Permission
        from django.contrib.contenttypes.models import ContentType
        from store.models import Order, OrderItem
        staff = User.objects.create_user("staff", "nhanvien@buildgear.vn", "123456", first_name="Nhân Viên", last_name="Kinh Doanh", is_staff=True)
        ctypes = ContentType.objects.get_for_models(Product, Order, OrderItem, Category, Brand).values()
        staff.user_permissions.set(Permission.objects.filter(content_type__in=ctypes))
        print("✅ Đã tạo Staff: staff / 123456")

    # Customer: customer / 123456
    if not User.objects.filter(username="customer").exists():
        User.objects.create_user("customer", "khachhang@gmail.com", "123456", first_name="Nguyễn Văn A")
        print("✅ Đã tạo Customer: customer / 123456")

    # 3. Tạo danh mục (Categories)
    categories_data = [
        ("CPU - Bộ vi xử lý", "Bộ vi xử lý trung tâm cho máy tính Intel và AMD"),
        ("VGA - Card màn hình", "Card đồ họa xử lý hình ảnh, chơi game, đồ họa"),
        ("Mainboard - Bo mạch chủ", "Bo mạch chủ kết nối các linh kiện"),
        ("RAM - Bộ nhớ trong", "RAM DDR4, DDR5 tốc độ cao cho PC"),
        ("Ổ cứng SSD / HDD", "Ổ cứng lưu trữ dữ liệu tốc độ cao NVMe, SATA"),
        ("PSU - Nguồn máy tính", "Nguồn cấp điện ổn định chuẩn 80 Plus"),
        ("Case - Vỏ máy tính", "Vỏ case kính cường lực, airflow thoáng mát"),
    ]
    cat_objs = {}
    for name, desc in categories_data:
        cat, _ = Category.objects.get_or_create(name=name, defaults={"description": desc})
        cat_objs[name] = cat
    print(f"✅ Đã tạo {len(cat_objs)} danh mục linh kiện.")

    # 4. Tạo thương hiệu (Brands)
    brands_data = ["Intel", "AMD", "NVIDIA", "ASUS", "MSI", "GIGABYTE", "Corsair", "Kingston"]
    brand_objs = {}
    for b_name in brands_data:
        brand, _ = Brand.objects.get_or_create(name=b_name)
        brand_objs[b_name] = brand
    print(f"✅ Đã tạo {len(brand_objs)} thương hiệu.")

    # 5. Tạo 7 linh kiện PC chính hãng ban đầu
    products_data = [
        {
            "name": "CPU Intel Core i5-13400F",
            "category": cat_objs["CPU - Bộ vi xử lý"],
            "brand": brand_objs["Intel"],
            "price": 5290000,
            "discount_price": 4890000,
            "stock_quantity": 20,
            "image_url": "/static/images/cpu-i5-13400f.svg",
            "specifications": "10 Nhân 16 Luồng, Turbo 4.60 GHz, 20MB Cache, Socket LGA 1700",
            "description": "CPU quốc dân tầm trung chơi game và làm việc cực mượt mà không lo giật lag.",
        },
        {
            "name": "CPU AMD Ryzen 5 7600",
            "category": cat_objs["CPU - Bộ vi xử lý"],
            "brand": brand_objs["AMD"],
            "price": 5990000,
            "discount_price": 5500000,
            "stock_quantity": 15,
            "image_url": "/static/images/cpu-r5-7600.svg",
            "specifications": "6 Nhân 12 Luồng, Turbo 5.1 GHz, 38MB Cache, Socket AM5",
            "description": "CPU thế hệ mới của AMD với kiến trúc Zen 4 mạnh mẽ, tối ưu hoá tối đa cho game thủ.",
        },
        {
            "name": "VGA ASUS Dual GeForce RTX 4060 EVO OC 8GB",
            "category": cat_objs["VGA - Card màn hình"],
            "brand": brand_objs["ASUS"],
            "price": 8890000,
            "discount_price": 8490000,
            "stock_quantity": 10,
            "image_url": "/static/images/vga-rtx4060-asus.svg",
            "specifications": "8GB GDDR6, 128-bit, PCIe 4.0, 2 Quạt tản nhiệt, DLSS 3",
            "description": "Card đồ họa bán chạy nhất phân khúc chiến game 1080p và 2K với công nghệ DLSS 3 siêu tốc.",
        },
        {
            "name": "Mainboard MSI B760M GAMING PLUS WIFI DDR5",
            "category": cat_objs["Mainboard - Bo mạch chủ"],
            "brand": brand_objs["MSI"],
            "price": 3890000,
            "discount_price": 3650000,
            "stock_quantity": 25,
            "image_url": "/static/images/main-msi-b760m.svg",
            "specifications": "Socket LGA 1700, 4 khe DDR5, PCIe 4.0, Wifi 6E tích hợp",
            "description": "Mainboard tầm trung tối ưu cho CPU Intel Gen 12, 13, 14 với tản nhiệt VRM dày dặn.",
        },
        {
            "name": "RAM Corsair Vengeance RGB 32GB (2x16GB) DDR5 6000MHz",
            "category": cat_objs["RAM - Bộ nhớ trong"],
            "brand": brand_objs["Corsair"],
            "price": 3490000,
            "discount_price": 3190000,
            "stock_quantity": 30,
            "image_url": "/static/images/ram-corsair-ddr5.svg",
            "specifications": "Kit 32GB (2x16GB), Bus 6000MHz, Chuẩn DDR5, Đèn LED RGB",
            "description": "RAM hiệu năng cao hỗ trợ Intel XMP 3.0 và AMD EXPO, hệ thống LED RGB rực rỡ.",
        },
        {
            "name": "Ổ cứng SSD Kingston NV2 1TB PCIe Gen4 NVMe M.2",
            "category": cat_objs["Ổ cứng SSD / HDD"],
            "brand": brand_objs["Kingston"],
            "price": 1790000,
            "discount_price": 1590000,
            "stock_quantity": 50,
            "image_url": "/static/images/ssd-kingston-1tb.svg",
            "specifications": "Dung lượng 1TB, Chuẩn NVMe Gen 4x4, Tốc độ đọc 3500MB/s, ghi 2100MB/s",
            "description": "Ổ cứng tốc độ cao khởi động hệ điều hành và tải game nặng trong tích tắc.",
        },
        {
            "name": "Nguồn Corsair CV650 650W 80 Plus Bronze",
            "category": cat_objs["PSU - Nguồn máy tính"],
            "brand": brand_objs["Corsair"],
            "price": 1590000,
            "discount_price": 1390000,
            "stock_quantity": 40,
            "image_url": "/static/images/psu-corsair-cv650.svg",
            "specifications": "Công suất 650W, Chuẩn 80 Plus Bronze, Quạt tản 120mm êm ái",
            "description": "Cung cấp nguồn điện ổn định cho hệ thống PC gaming hiện đại.",
        },
    ]

    for p_data in products_data:
        p, created = Product.objects.get_or_create(
            name=p_data["name"],
            defaults=p_data
        )
        if created:
            print(f"  + Đã thêm sản phẩm: {p.name}")

    print("\n🎉 Khởi tạo CSDL SQLite và dữ liệu mẫu thành công 100%!")

if __name__ == "__main__":
    run_seed()
