# config/settings.py
from pathlib import Path
import os

# 构建项目路径，例如：BASE_DIR / 'subdir'
BASE_DIR = Path(__file__).resolve().parent.parent

# 快速开发环境设置 - 不适合生产环境
# 更多信息请参考：
# https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# 安全警告：请勿在生产环境中泄露密钥！
SECRET_KEY = '防止泄露秘钥'

# 安全警告：不要在生产环境中开启调试模式！
DEBUG = True

ALLOWED_HOSTS = [ ]#填写自己的域名

CSRF_TRUSTED_ORIGINS = [

]

# 应用定义
INSTALLED_APPS = [
    'simpleui',  # django-simpleui美化管理界面
    'django.contrib.admin',  # Django管理后台
    'django.contrib.auth',  # 用户认证系统
    'django.contrib.contenttypes',  # 内容类型框架
    'django.contrib.sessions',  # 会话框架
    'django.contrib.messages',  # 消息框架
    'django.contrib.staticfiles',  # 静态文件支持
    'rest_framework',  # Django REST Framework
    'constance',  # 动态配置
    'constance.backends.database',  # 数据库存储后端

    'ai_app',
]



MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',  # 安全中间件
    'django.contrib.sessions.middleware.SessionMiddleware',  # 会话中间件
    'django.middleware.common.CommonMiddleware',  # 通用中间件
    'django.middleware.csrf.CsrfViewMiddleware',  # CSRF保护中间件
    'django.contrib.auth.middleware.AuthenticationMiddleware',  # 认证中间件
    'django.contrib.messages.middleware.MessageMiddleware',  # 消息中间件
    'django.middleware.clickjacking.XFrameOptionsMiddleware',  # 防止点击劫持
]

ROOT_URLCONF = 'config.urls'  # 根URL配置

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',  # 模板引擎
        'DIRS': [
            # 添加应用的模板目录
            os.path.join(BASE_DIR, 'ai_app/templates'),
        ],
        'APP_DIRS': True,  # 是否自动查找应用中的模板
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',  # 调试上下文处理器
                'django.template.context_processors.request',  # 请求上下文处理器
                'django.contrib.auth.context_processors.auth',  # 用户认证上下文处理器
                'django.contrib.messages.context_processors.messages',  # 消息上下文处理器
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'  # WSGI应用入口

# 数据库配置
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': ' ',
        'USER': ' ',
        'PASSWORD': ' ',
        'HOST': ' ',
        'PORT': ' ',
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': 'SET default_storage_engine=INNODB;'
        }
    }
}

# 密码验证
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',  # 验证密码与用户属性相似性
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',  # 最小长度验证
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',  # 常见密码验证
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',  # 数字密码验证
    },
]

# 国际化
# https://docs.djangoproject.com/en/5.1/topics/i18n/
LANGUAGE_CODE = 'zh-Hans'  # 语言代码：简体中文
TIME_ZONE = 'Asia/Shanghai'  # 时区：上海
USE_I18N = True  # 启用国际化
USE_TZ = False  # 关闭时区支持

# 媒体文件配置
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# 确保上传目录存在
UPLOAD_ROOT = os.path.join(MEDIA_ROOT, 'uploads')
if not os.path.exists(UPLOAD_ROOT):
    os.makedirs(UPLOAD_ROOT)

# 静态文件配置
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# 默认主键字段类型
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'  # 默认自增主键类型

# Constance 动态配置
CONSTANCE_CONFIG = {
    'WECHAT_APP_ID': (' ', '微信小程序 AppID / WeChat Mini Program AppID'),
    'WECHAT_APP_SECRET': (' ', '微信小程序 AppSecret / WeChat Mini Program AppSecret'),
    'WECHAT_MCH_ID': (' ', '微信商户号 / WeChat Merchant ID'),
    'WECHAT_MCH_KEY': (' ', '微信商户密钥 / WeChat Merchant Key'),
    'WECHAT_NOTIFY_URL': (' ', '微信支付通知地址 / WeChat Payment Notify URL'),
    'API_TIMEOUT': (30, '接口请求超时时间（单位：秒）'),
    'GLM_API_KEY': (' ', 'GLM API密钥'),
    'COZE_API_TOKEN': (' ', 'COZE API令牌'),
    'COZE_BOT_ID': (' ', 'COZE 机器人ID'),
    'QWEN_API_KEY': (' ', 'Qwen API密钥'),
    'DEFAULT_VOICE': (' ', '默认语音角色'),
    'DEFAULT_VIDEO_SIZE': ('720x480', '默认视频尺寸'),
    'DEFAULT_VIDEO_FPS': (30, '默认视频帧率'),
    'MAX_TOKENS': (1024, '最大token数量'),
    'QWEN_APP_ID': (' ', '千问应用ID/Qwen App ID'),
    'QWEN_Deeskeep_ID':(' ','千问deeskeep应用ID/Qwen Deeskeep App ID')
}

# Constance 配置后端
CONSTANCE_BACKEND = 'constance.backends.database.DatabaseBackend'

# Constance 配置分组
CONSTANCE_CONFIG_FIELDSETS = {
    # '基础配置': ['API_TIMEOUT', 'DEFAULT_VOICE', 'DEFAULT_VIDEO_SIZE', 'DEFAULT_VIDEO_FPS', 'MAX_TOKENS'],
    # 'API密钥配置': ['GLM_API_KEY', 'COZE_API_TOKEN', 'COZE_BOT_ID', 'QWEN_API_KEY', 'QWEN_APP_ID'],
    # '微信配置': ['WECHAT_APP_ID', 'WECHAT_APP_SECRET', 'WECHAT_MCH_ID', 'WECHAT_MCH_KEY', 'WECHAT_NOTIFY_URL'],
}

# 配置文件本地存储
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

# 登录相关配置
LOGIN_URL = '/admin/login/'
LOGIN_REDIRECT_URL = '/admin/'
LOGOUT_REDIRECT_URL = '/admin/login/'

# 会话设置
SESSION_COOKIE_AGE = 1209600  # 2周
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# 认证后端
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]


WECHAT_SITE_HOST = '填写自己的域名'  # 你的域名
WECHAT_SITE_HTTPS = False  # 开发环境可以设置为 False

# 日志配置
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}

# 在开发环境中添加以下配置

CORS_ALLOW_ALL_ORIGINS = True  # 允许所有域名跨域访问
DEBUG = True  # 开启调试模式
