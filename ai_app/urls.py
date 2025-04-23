# ai_app/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from django.views.decorators.csrf import csrf_exempt
from .views import (
    GLM4View, 
    GLM4VView, 
    GLMCogView, 
    CogVideoXView, 
    GLM4Voice,
    CozeChatView,
    api_docs,
    QwenChat,
    QwenChatFile,
    QwenChatToke,
    QwenOCR,
    Qwenomni,
    QwenAudio,
    FileUploadView,
    Qwenvl,
    deeskeep,
)
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # path('api/', include(router.urls)),
    path('api-docs/', views.api_docs, name='api_docs'),#说明文档页面
    path('', api_docs, name='api-docs'),#说明文档页面
    path('GLM-4/', GLM4View.as_view(), name='glm-4-api'),
    path('GLM-4V/', GLM4VView.as_view(), name='glm-4v-api'),
    path('GLM-Cog/', GLMCogView.as_view(), name='glm-cog-api'),
    path('GLM-CogVideo/', CogVideoXView.as_view(), name='glm-cogvideo-api'),
    path('GLM-4-Voice/', GLM4Voice.as_view(), name='glm-4-voice-api'),
    path('CozeChat/', CozeChatView.as_view(), name='coze-chat-api'),
    path('QwenChat/', QwenChat.as_view(), name='qwen-chat-api'),
    path('QwenChatFile/', QwenChatFile.as_view(), name='qwen-chat-file-api'),
    path('QwenChatToke/', QwenChatToke.as_view(), name='qwen-chat-toke-api'),
    path('QwenOCR/', QwenOCR.as_view(), name='qwen-ocr-api'),
    path('Qwenomni/', Qwenomni.as_view(), name='qwen-omni-api'),
    path('QwenAudio/', QwenAudio.as_view(), name='qwen-audio-api'),
    path('upload/', FileUploadView.as_view(), name='file-upload'),
    path('Qwenvl/', Qwenvl.as_view(), name='qwen-vl-api'),
    path('deeskeep/', deeskeep.as_view(), name='qwen-deeskeep-api'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  # 添加媒体文件服务