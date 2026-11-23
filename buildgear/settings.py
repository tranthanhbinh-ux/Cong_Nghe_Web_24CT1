from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-buildgear-secret-key-super-secure-change-in-prod')

DEBUG = 'RENDER' not in os.environ

ALLOWED_HOSTS = ['*']
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'store.apps.StoreConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'buildgear.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'store.context_processors.cart_count',
            ],
        },
    },
]

WSGI_APPLICATION = 'buildgear.wsgi.application'

DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    try:
        import dj_database_url
        DATABASES = {
            'default': dj_database_url.config(
                default=DATABASE_URL,
                conn_max_age=600,
                conn_health_checks=True,
                ssl_require=True,
            )
        }
    except Exception:
        pass
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'buildgear_db',
            'USER': 'root',
            'PASSWORD': '',
            'HOST': '127.0.0.1',
            'PORT': '3306',
            'OPTIONS': {
                'charset': 'utf8mb4',
                'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            }
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
]

LANGUAGE_CODE = 'vi'
TIME_ZONE = 'Asia/Ho_Chi_Minh'
USE_I18N = True
USE_TZ = True
USE_THOUSAND_SEPARATOR = True
FORMAT_MODULE_PATH = [
    'buildgear.formats',
]

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'store' / 'static',
]
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'home'

# Jazzmin Admin Theme Settings
JAZZMIN_SETTINGS = {
    "site_title": "BuildGear Admin",
    "site_header": "BuildGear PC Admin",
    "site_brand": "⚡ BuildGear PC",
    "welcome_sign": "Hệ Thống Quản Trị Trung Tâm - BuildGear PC",
    "copyright": "BuildGear PC Gaming & Workstation",
    "search_model": ["store.Product", "store.Order"],
    
    # Top navigation links
    "topmenu_links": [
        {"name": "Trang chủ bán hàng", "url": "home", "new_window": True},
        {"name": "Đơn hàng", "url": "admin:store_order_changelist"},
        {"name": "Kho linh kiện", "url": "admin:store_product_changelist"},
    ],

    # User menu
    "usermenu_links": [
        {"name": "Xem website", "url": "home", "new_window": True, "icon": "fas fa-external-link-alt"},
    ],

    "show_sidebar": True,
    "navigation_expanded": True,
    "hide_apps": [],
    "hide_models": [],
    
    # Custom icons for models
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user-shield",
        "auth.Group": "fas fa-users",
        "store.Category": "fas fa-th-large",
        "store.Brand": "fas fa-copyright",
        "store.Product": "fas fa-microchip",
        "store.Order": "fas fa-shopping-bag",
        "store.OrderItem": "fas fa-box-open",
    },
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-dot-circle",
    
    # Related modal
    "related_modal_active": True,
    "custom_css": "css/admin_custom.css",
    "custom_js": None,
    "use_google_fonts_cdn": True,
    "show_ui_builder": False,
    
    "order_with_respect_to": ["store", "store.Order", "store.Product", "store.Category", "store.Brand", "auth"],
}

# Cyber / Tech Dark UI Theme
JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-dark",
    "accent": "accent-info",
    "navbar": "navbar-dark navbar-navy",
    "no_navbar_border": True,
    "navbar_fixed": True,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": True,
    "sidebar": "sidebar-dark-info",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": True,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "darkly",
    "theme_mode": "dark",
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success"
    }
}

