# ai
from django.contrib.auth.models import User, AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
import os
import mimetypes
from django.contrib.auth import get_user_model

# 模型信息表
class ModelInfo(models.Model):
    ''' 
    模型信息表，用于存储AI模型的基本信息
    '''
    MODEL_TYPES = (
        ('chat', '大语言模型'),
        ('vision', '多模态模型'),
        ('ocr', '文字识别'),
        ('file', '文档理解'),
        ('audio', '语音理解')
    )

    model = models.TextField(verbose_name="模型标识")
    name = models.TextField(verbose_name="模型名称")
    type = models.CharField(
        max_length=20,
        choices=MODEL_TYPES,
        default='chat',
        verbose_name="模型类型"
    )
    context = models.TextField(verbose_name="模型描述")
    cost = models.TextField(verbose_name="费用说明")
    api_endpoint = models.CharField(
        max_length=255,
        verbose_name="接口路径",
        default='/api/vision/'
    )
    
    def __str__(self):
        return f"{self.name} - {self.model} - {self.type} - {self.context} - {self.cost}"
    
    class Meta:
        db_table = "ai_model_info"
        verbose_name = "所有接口配置"
        verbose_name_plural = verbose_name

# 媒体资料列表
class UploadedFile(models.Model):
    """上传文件模型"""
    FILE_TYPES = (
        ('image', '图片'),
        ('audio', '音频'),
        ('video', '视频'),
        ('document', '文档'),
        ('other', '其他')
    )

    file = models.FileField(
        upload_to='uploads/%Y/%m/%d/',
        verbose_name="文件"
    )
    file_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="文件名"
    )
    file_type = models.CharField(
        max_length=20,
        choices=FILE_TYPES,
        editable=False,
        verbose_name="文件类型"
    )
    file_size = models.IntegerField(
        verbose_name="文件大小(字节)"
    )
    mime_type = models.CharField(
        max_length=100,
        verbose_name="MIME类型"
    )
    upload_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name="上传时间"
    )
    uploader = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        verbose_name="上传者",
        related_name='uploaded_files',
        default=1  # 设置默认用户ID
    )
    
    def save(self, *args, **kwargs):
        if not self.file_name:
            self.file_name = os.path.basename(self.file.name)
        else:
            # 如果指定了新文件名，保持原扩展名
            original_ext = os.path.splitext(self.file.name)[1]
            new_name = os.path.splitext(self.file_name)[0]
            self.file_name = f"{new_name}{original_ext}"
        
        # 自动判断文件类型
        ext = os.path.splitext(self.file.name)[1].lower()
        if ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']:
            self.file_type = 'image'
        elif ext in ['.mp3', '.wav', '.ogg', '.m4a', '.flac']:
            self.file_type = 'audio'
        elif ext in ['.mp4', '.avi', '.mov', '.wmv', '.mkv', '.webm']:
            self.file_type = 'video'
        elif ext in ['.pdf', '.doc', '.docx', '.txt', '.md', '.markdown']:
            self.file_type = 'document'
        else:
            self.file_type = 'other'
            
        # 设置文件大小
        if not self.file_size:
            self.file_size = self.file.size
            
        # 设置MIME类型
        if not self.mime_type:
            mime_type, _ = mimetypes.guess_type(self.file.name)
            self.mime_type = mime_type or 'application/octet-stream'
            
        super().save(*args, **kwargs)

    def __str__(self):
        return self.file_name

    class Meta:
        db_table = 'ai_app_uploadedfile'  # 指定表名
        verbose_name = "多媒体资料"
        verbose_name_plural = verbose_name
        ordering = ['-upload_time']


