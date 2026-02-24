from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
# DEBUG = os.getenv("DEBUG", "False")だけではDjangoは文字列の"False"を受け取ってしまって、boolianのFalseにならない
DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")

# .env.prodのスペース対策
ALLOWED_HOSTS = [
    host.strip()
    for host in os.getenv("ALLOWED_HOSTS", "").split(",")
    if host.strip()
]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'accounts',
    'analysis',
    'spaces',
    'teams',
    "storages",
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR, 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'config.context_processors.header_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv("DATABASE_NAME"),
        'USER': os.getenv("DATABASE_USER"),
        'PASSWORD': os.getenv("DATABASE_PASSWORD"),
        'HOST': os.getenv("DATABASE_HOST"),
        'PORT': os.getenv("DATABASE_PORT", "3306"),
    }
}

AUTH_USER_MODEL = 'accounts.CustomUser'
# LOGIN_URL = "accounts:login"
LOGOUT_REDIRECT_URL = "accounts:login"

# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'ja'

TIME_ZONE = 'Asia/Tokyo'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

# 各アプリのstaticを読み込む
# STATIC_URL = '/static/'
# config/staticを読み込む    
STATICFILES_DIRS = [
    BASE_DIR / "static",  
]
# ↓デプロイ時のcollectstatic用
STATIC_ROOT = BASE_DIR / "staticfiles"

AWS_CLOUDFRONT_DNS = os.getenv("AWS_CLOUDFRONT_DNS")
AWS_S3_REGION_NAME = os.getenv("AWS_S3_REGION_NAME", "ap-northeast-1")

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "config.storages.StaticStorage",
        "OPTIONS": {
            "bucket_name": os.getenv("AWS_STORAGE_BUCKET_NAME"),
            "location": "static",
        },
    },
}

STATIC_URL = f"https://{AWS_CLOUDFRONT_DNS}/static/"

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# POST処理を信用していいオリジンの指定
CSRF_TRUSTED_ORIGINS = os.getenv("CSRF_TRUSTED_ORIGINS","").split(",")

# 'https://teamy-profile.com'を入力して最初に表示されるページへの自動遷移。topならtopに変える。
LOGIN_URL = "/top/"

# sessionIDを含むCookieをHTTPSの時だけ許可する
SESSION_COOKIE_SECURE = not DEBUG

# CSRFトークンを含むCookieをHTTPSの時だけ許可する
CSRF_COOKIE_SECURE = not DEBUG

# ALBがHTTPSをHTTPとして通信しているので、Djangoに元はHTTPSと信じさせる＋万一スルーされたらhttpはリダイレクトさせる
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# クライアントがアクセスしてきたHOST名をX_Forwarded_Hostヘッダーから取得する
USE_X_FORWARDED_HOST = True

# HSTS(ブラウザにHTTPSでアクセスすべきサイトだと覚えさせる時間と、サブドメインアクセスでも有効にする))
SECURE_HSTS_SECONDS = 3600
SECURE_HSTS_INCLUDE_SUBDOMAINS = True

# ブラウザが勝手にContent-Typeを推測するのを防ぐ
SECURE_CONTENT_TYPE_NOSNIFF = True

# デフォルトもDENYであるが明示的に表示
X_FRAME_OPTIONS = 'DENY'

# 他人がアプリ内のログイン後のURLなどをそのままコピペしてリンクとしても、リンクとしてはteamy-profile.comに飛ぶ
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

# デフォルトでも'Lax'ではあるが将来性のために明示。sessionIDとCSRFトークンをGETなら送る、POSTなら送らない
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SAMESITE = 'Lax'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': './django_error.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}