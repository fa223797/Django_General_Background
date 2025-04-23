from django.contrib import admin
from .models import ModelInfo, UploadedFile
from constance.admin import ConstanceAdmin, Config, ConstanceForm
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.urls import reverse, path
from django.http import HttpResponse, HttpResponseRedirect
import os
from django.conf import settings
from django.shortcuts import render
from django.contrib.auth.admin import UserAdmin
import csv
from datetime import datetime
from django.db.models import Sum, F, Func
from django.db.models.functions import Cast
from django.db.models import IntegerField

# 自定义 Constance 的 Admin 配置
class CustomConstanceAdmin(ConstanceAdmin):
    # 定义不可编辑的配置项
    readonly_config_fields = {
        'WECHAT_APP_ID',
        'WECHAT_APP_SECRET',
        'WECHAT_MCH_ID',
        'WECHAT_MCH_KEY',
        'WECHAT_NOTIFY_URL',
    }

    def get_config_value(self, name, options, form, initial):
        config = super().get_config_value(name, options, form, initial)
        if isinstance(config, dict) and 'value' in config:
            # 移除默认值显示
            config.pop('default', None)
            # 如果是只读配置项，禁用输入
            if name in self.readonly_config_fields:
                if config.get('field'):
                    config['field'].widget.attrs['readonly'] = True
                    config['field'].widget.attrs['class'] = 'readonly-field'
            # 调整输入框宽度
            if config.get('field'):
                config['field'].widget.attrs['style'] = 'width: 50%;'
        return config

    def get_changelist_form(self, request, **kwargs):
        form = super().get_changelist_form(request, **kwargs)
        field_labels = {
            'WECHAT_APP_ID': "微信小程序 AppID",
            'API_TIMEOUT': "接口超时时间（秒）",
            'GLM_API_KEY': "智谱AI API密钥",
            'COZE_API_TOKEN': "COZE API令牌",
            'COZE_BOT_ID': "COZE 机器人ID",
            'QWEN_API_KEY': "通义千问 API密钥",
            'DEFAULT_VOICE': "默认语音角色",
            'DEFAULT_VIDEO_SIZE': "默认视频尺寸",
            'DEFAULT_VIDEO_FPS': "默认视频帧率",
            'MAX_TOKENS': "最大Token数量",
        }
        
        for field_name, label in field_labels.items():
            if field_name in form.base_fields:
                form.base_fields[field_name].label = label
        return form

    class Media:
        css = {
            'all': ('admin/css/custom_constance.css',)
        }

    def has_change_permission(self, request, obj=None):
        if obj and obj.key in self.readonly_config_fields:
            return False
        return super().has_change_permission(request, obj)

    change_list_template = 'admin/constance/change_list.html'
    change_list_form = ConstanceForm
    change_list_title = '参数配置'

# 重新注册 Constance Config
admin.site.unregister([Config])
admin.site.register([Config], CustomConstanceAdmin)

# 修改 admin 站点标题
admin.site.site_header = '玫云科技AI管理后台'
admin.site.site_title = '系统管理'
admin.site.index_title = '系统管理'
admin.site.empty_value_display = '无数据'#空数据显示内容


# 模型信息表
@admin.register(ModelInfo)
class ModelInfoAdmin(admin.ModelAdmin):
    """
    AI模型信息的Admin配置
    """
    # 在列表页显示的字段
    list_display = ('name', 'model', 'type', 'context', 'cost')

    # 添加搜索框，支持按模型标识和模型名称搜索
    search_fields = ('name', 'model')

    # 添加过滤器，支持按模型类型过滤
    list_filter = ('type',)

    # 设置默认排序规则（按模型名称升序）
    ordering = ('name',)

    # 在编辑页分组显示字段
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'model', 'type')
        }),
        ('详细信息', {
            'fields': ('context', 'cost')
        })
    )

    change_list_template = 'admin/model_info_change_list.html'

    def changelist_view(self, request, extra_context=None):
        # 重定向到api_docs页面
        return render(request, 'api_docs.html', {'models': ModelInfo.objects.all()})

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('api-docs/', self.admin_site.admin_view(self.changelist_view), name='model_info_api_docs'),
        ]
        return custom_urls + urls

    class Media:
        css = {
            'all': ('admin/css/api_docs.css',)
        }

# 媒体资料列表
@admin.register(UploadedFile)
class UploadedFileAdmin(admin.ModelAdmin):
    """上传文件管理"""
    list_display = ('file_name', 'file_type', 'file_size_display', 'mime_type', 'upload_time', 'uploader', 'file_preview', 'file_actions')
    list_filter = ('file_type', 'upload_time', 'uploader')
    search_fields = ('file_name', 'uploader__username')
    readonly_fields = ('file_size', 'mime_type', 'upload_time', 'file_type')
    
    def get_queryset(self, request):
        # 按文件类型分组排序
        return super().get_queryset(request).order_by('file_type', '-upload_time')
    
    def file_size_display(self, obj):
        """格式化文件大小显示"""
        if obj.file_size < 1024:
            return f"{obj.file_size} B"
        elif obj.file_size < 1024 * 1024:
            return f"{obj.file_size/1024:.2f} KB"
        elif obj.file_size < 1024 * 1024 * 1024:
            return f"{obj.file_size/(1024*1024):.2f} MB"
        return f"{obj.file_size/(1024*1024*1024):.2f} GB"
    
    file_size_display.short_description = '文件大小'

    def file_actions(self, obj):
        """文件操作按钮"""
        return format_html(
            '<a class="button" href="{}">下载</a>&nbsp;'
            '<button class="button" onclick="renameFile({})">重命名</button>&nbsp;'
            '<button class="button" onclick="deleteFile({})">删除</button>',
            obj.file.url,
            obj.pk,
            obj.pk
        )
    file_actions.short_description = '操作'

    def file_preview(self, obj):
        """文件预览"""
        if obj.file_type == 'image':
            return format_html(
                '<img src="{}" style="max-width:100px; max-height:100px"/>',
                obj.file.url
            )
        elif obj.file_type == 'video':
            return format_html(
                '<video width="100" height="100" controls>'
                '<source src="{}" type="{}">不支持预览</video>',
                obj.file.url, obj.mime_type
            )
        elif obj.file_type == 'audio':
            return format_html(
                '<audio controls style="width:200px">'
                '<source src="{}" type="{}">不支持预览</audio>',
                obj.file.url, obj.mime_type
            )
        elif obj.file_type == 'document':
            if obj.file_name.lower().endswith(('.md', '.markdown')):
                return format_html(
                    '<a href="{}" target="_blank">预览Markdown</a>',
                    obj.file.url
                )
            return format_html(
                '<a href="{}" target="_blank">查看文档</a>',
                obj.file.url
            )
        return format_html('<a href="{}" target="_blank">下载文件</a>', obj.file.url)
    
    file_preview.short_description = '预览'

    def delete_file(self, request, file_id):
        """删除文件"""
        try:
            uploaded_file = self.get_object(request, file_id)
            if uploaded_file:
                # 删除物理文件
                file_path = os.path.join(settings.MEDIA_ROOT, str(uploaded_file.file))
                if os.path.exists(file_path):
                    os.remove(file_path)
                # 删除数据库记录
                uploaded_file.delete()
                return HttpResponse('文件删除成功')
            return HttpResponse('文件不存在', status=404)
        except Exception as e:
            return HttpResponse(f'删除失败: {str(e)}', status=500)

    def download_file(self, request, file_id):
        """下载文件"""
        uploaded_file = self.get_object(request, file_id)
        if uploaded_file is None:
            return HttpResponse('文件不存在', status=404)
            
        file_path = os.path.join(settings.MEDIA_ROOT, str(uploaded_file.file))
        if os.path.exists(file_path):
            with open(file_path, 'rb') as fh:
                response = HttpResponse(fh.read(), content_type=uploaded_file.mime_type)
                response['Content-Disposition'] = f'attachment; filename={uploaded_file.file_name}'
                return response
        return HttpResponse('文件不存在', status=404)

    def rename_file(self, request, file_id):
        """重命名文件"""
        if request.method == 'POST':
            uploaded_file = self.get_object(request, file_id)
            new_name = request.POST.get('new_name')
            if uploaded_file and new_name:
                # 保持原扩展名
                old_ext = os.path.splitext(uploaded_file.file_name)[1]
                new_name = f"{new_name}{old_ext}"
                uploaded_file.file_name = new_name
                uploaded_file.save()
                self.message_user(request, '文件重命名成功')
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        return HttpResponse('重命名失败', status=400)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:file_id>/delete/',
                self.admin_site.admin_view(self.delete_file),
                name='uploaded-file-delete',
            ),
            path(
                '<int:file_id>/rename/',
                self.admin_site.admin_view(self.rename_file),
                name='uploaded-file-rename',
            ),
            path(
                '<int:file_id>/download/',
                self.admin_site.admin_view(self.download_file),
                name='uploaded-file-download',
            ),
        ]
        return custom_urls + urls

    class Media:
        js = (
            'https://code.jquery.com/jquery-3.6.0.min.js',
            'admin/js/file_admin.js',
        )

    def save_model(self, request, obj, form, change):
        if not change:  # 如果是新建记录
            obj.uploader = request.user  # 设置当前用户为上传者
        super().save_model(request, obj, form, change)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "uploader":
            kwargs["initial"] = request.user.id  # 设置默认值为当前用户
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

