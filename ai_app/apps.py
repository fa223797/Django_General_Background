from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class AiAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ai_app'
    verbose_name = 'AI配置及媒体资源'
    verbose_name_plural = 'AI配置及媒体资源'
    
    def ready(self):
        # 导入必要的模块
        from django.contrib import admin
        from django.contrib.admin.sites import AlreadyRegistered, NotRegistered
        
        # 获取我们的自定义用户模型管理类
        # from ai_app.models import CustomUser
        
        # 尝试将自定义用户模型显示在"认证和授权"组下
        try:
            # 创建一个admin_utils.py文件，并在其中添加以下代码
            # 这个文件可以在任何导入时刻都能加载
            from django.contrib.admin.sites import site
            
            # 以下代码尝试将CustomUser模型移动到auth应用组
            # 注意：这是一个hack方式，取决于Django内部实现
            # 可能在未来Django版本中不再工作
            # if hasattr(admin.site, '_registry'):
            #     if CustomUser in admin.site._registry:
            #         model_admin = admin.site._registry[CustomUser]
            #         if hasattr(model_admin, 'model'):
            #             admin.site._registry[CustomUser].model._meta.app_label = 'auth'
        except Exception as e:
            # 如果出现错误，记录日志但不引发异常
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"无法将CustomUser移动到'认证和授权'组: {e}")


