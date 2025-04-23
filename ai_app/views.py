# views.py
from django.shortcuts import render  # 导入Django的render函数用于渲染页面模板
from rest_framework.views import APIView  # 导入DRF的APIView类，用于创建API视图
from rest_framework.response import Response  # 导入DRF的Response对象，用于构建HTTP响应
from rest_framework import status  # 导入DRF的状态码模块，便于返回标准HTTP状态码
import requests  # 导入requests库，用于发送HTTP请求
import json  # 导入json库，用于处理JSON数据
import base64  # 导入base64库，用于处理Base64编码
from zhipuai import ZhipuAI  # 导入ZhipuAI库，用于调用智谱AI的API
from cozepy import Coze, TokenAuth, Message, ChatEventType
from dashscope import Generation 
from django.http  import StreamingHttpResponse, JsonResponse 
from openai import OpenAI
from pathlib import Path
import dashscope
import os
import logging
from rest_framework.decorators import action
import traceback
from constance import config
import mimetypes
from rest_framework.parsers import MultiPartParser
from ai_app.models import ModelInfo, UploadedFile


logger = logging.getLogger(__name__)

# ===============后台功能类模块===============
# # 说明文档页面
def api_docs(request):
    """API文档页面"""
    models = ModelInfo.objects.all()
    return render(request, 'api_docs.html', {'models': models})
# 媒体资料管理
class FileUploadView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request, *args, **kwargs):
        # 获取上传的文件
        uploaded_file = request.FILES.get('file')
        if not uploaded_file:
            return Response({'error': '未提供文件'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 获取用户ID或用户名
            user_id = request.data.get('user_id')
            username = request.data.get('username')
            if user_id or username:
                # 通过API上传，使用传入的用户ID或用户名
                pass  # 删除的代码块
            else:
                # 通过网页上传，使用当前登录用户
                if not request.user.is_authenticated:
                    return Response({'error': '未登录'}, status=status.HTTP_401_UNAUTHORIZED)
                uploader = request.user

            # 创建UploadedFile实例
            uploaded_file_instance = UploadedFile(
                file=uploaded_file,
                uploader=uploader
            )
            
            # 自动填充其他字段
            uploaded_file_instance.file_name = os.path.basename(uploaded_file.name)
            uploaded_file_instance.file_size = uploaded_file.size
            
            # 自动判断MIME类型
            mime_type, _ = mimetypes.guess_type(uploaded_file.name)
            uploaded_file_instance.mime_type = mime_type or 'application/octet-stream'
            
            # 保存实例，save方法会自动处理文件类型分类
            uploaded_file_instance.save()
            
            # 返回成功响应
            return Response({
                'id': uploaded_file_instance.id,
                'file_name': uploaded_file_instance.file_name,
                'file_type': uploaded_file_instance.file_type,
                'file_size': uploaded_file_instance.file_size,
                'mime_type': uploaded_file_instance.mime_type,
                'upload_time': uploaded_file_instance.upload_time,
                'file_url': uploaded_file_instance.file.url,
                'uploader_id': uploader.id
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



# ===============模型接口===============
# GLM模型
# GLM语言模型chat类型，glm-4
class GLM4View(APIView):
    def post(self, request):
        """
        处理POST请求，调用GLM（Generative Language Model）服务并返回结果。
        """
        # 定义GLM服务的URL地址
        glm_url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
        
        # 从请求的数据中获取用户的问题，默认为空字符串
        question = request.data.get('question', '')
        
        # 从请求的数据中获取要使用的模型名称
        model_name = request.data.get('model')  # 直接使用传入的模型名称
        
        # 如果问题为空，则返回错误信息并设置HTTP状态码为400 Bad Request
        if not question:
            return Response({"error": "question is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        # 构造发送到GLM API的头部信息，包括授权和内容类型
        headers = {
            "Authorization": f"Bearer {config.GLM_API_KEY}",  # 使用API密钥进行身份验证
            "Content-Type": "application/json",     # 指定请求体的内容类型为JSON
        }
        
        # 构建发送给GLM API的请求数据
        data = {
            "model": model_name,  # 请求中指定要使用的模型名称
            
            # 用户的消息部分，包含角色（这里是用户）和具体问题内容
            "messages": [{"role": "user", "content": question}],
            
            # 工具配置：这里指定了一个检索工具
            "tools": [
                {
                    "type": "retrieval",  # 工具类型是"检索"
                    
                    # 具体的检索配置：
                    "retrieval": {
                        "knowledge_id": " ",  # 知识库ID
                        
                        # 提示模板，告诉模型如何处理检索到的信息
                        "prompt_template": (
                            "从\n\"\"\"\n{{knowledge}}\n\"\"\"\n中找问题\n\"\"\"\n{{question}}\n\"\"\"\n的答案，如果有对应的答案则用内容回复，没有找到的话就用最有温度的聊天和我对话，不要重复直接回答"
                        )
                    }
                }
            ]
        }

        try:
            # 尝试通过requests库发起一个POST请求到GLM API服务器
            response = requests.post(glm_url, headers=headers, json=data)
            
            # 检查API响应的状态码是否在成功范围内（如2xx）。如果不是，则引发HTTPError异常
            response.raise_for_status()
            
            # 返回API的成功响应数据，并将HTTP状态码设为200 OK
            return Response(response.json(), status=status.HTTP_200_OK)
        
        except requests.exceptions.RequestException as e:
            # 如果发生任何与网络请求相关的错误（例如连接失败、超时等），捕获这些异常并返回详细的错误信息，
            # 同时设置HTTP状态码为503 Service Unavailable表示临时不可用的服务端问题。
            return Response(
                {"error": f"API request failed: {str(e)}"}, 
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        except json.JSONDecodeError:
            # 当API返回的数据不是有效的JSON格式时，会抛出json.JSONDecodeError异常；
            # 这里我们捕捉此异常，并告知客户端API响应格式无效，同时设置HTTP状态码为502 Bad Gateway表示网关或代理收到上游服务器的有效响应但是无法解析它。
            return Response(
                {"error": "Invalid API response format"}, 
                status=status.HTTP_502_BAD_GATEWAY
            )
# GLM语言模型多模态识别glm-4v模型
class GLM4VView(APIView):
    def post(self, request):
        glm_url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
        
        # 直接获取完整的messages结构
        messages = request.data.get('messages', [])
        model_name = request.data.get('model', 'glm-4v-flash')

        # 基本验证
        if not messages:
            return Response({"error": "messages is required"}, status=status.HTTP_400_BAD_REQUEST)

        headers = {
            "Authorization": f"Bearer {config.GLM_API_KEY}",
            "Content-Type": "application/json",
        }
        
        data = {
            "model": model_name,
            "messages": messages  # 直接使用客户端传来的messages结构
        }

        try:
            response = requests.post(glm_url, headers=headers, json=data)
            response.raise_for_status()
            return Response(response.json(), status=status.HTTP_200_OK)
            
        except requests.exceptions.RequestException as e:
            return Response({"error": str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except json.JSONDecodeError:
            return Response({"error": "Invalid API response format"}, status=status.HTTP_502_BAD_GATEWAY)
# GLM文生图模型glm-CogView
class GLMCogView(APIView):
    def post(self, request):
        cog_url = "https://open.bigmodel.cn/api/paas/v4/images/generations"
        
        # 获取参数
        model_name = request.data.get('model', 'cogview-3')
        prompt = request.data.get('prompt', '')
        size = request.data.get('size', '1024x1024')  # 默认尺寸
        user_id = request.data.get('user_id', '')  # 可选参数
        
        # 基本验证
        if not prompt:
            return Response({"error": "prompt is required"}, status=status.HTTP_400_BAD_REQUEST)
            
        headers = {
            "Authorization": f"Bearer {config.GLM_API_KEY}",
            "Content-Type": "application/json",
        }
        
        data = {
            "model": model_name,
            "prompt": prompt
        }
        
        # 添加可选参数
        if size:
            data["size"] = size
        if user_id:
            data["user_id"] = user_id

        try:
            response = requests.post(cog_url, headers=headers, json=data)
            response.raise_for_status()
            return Response(response.json(), status=status.HTTP_200_OK)
            
        except requests.exceptions.RequestException as e:
            return Response({"error": str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except json.JSONDecodeError:
            return Response({"error": "Invalid API response format"}, status=status.HTTP_502_BAD_GATEWAY)
# GLM文生视频模型CogVideoX
class CogVideoXView(APIView):
    def post(self, request):
        """生成视频请求"""
        try:
            # 初始化智谱AI客户端
            client = ZhipuAI(api_key=config.GLM_API_KEY)
            
            if request.data.get('action') == 'check_status':
                # 查询任务状态
                task_id = request.data.get('task_id')
                if not task_id:
                    return Response({"error": "task_id is required"}, status=status.HTTP_400_BAD_REQUEST)
                    
                response = client.videos.retrieve_videos_result(id=task_id)
                
                # 直接返回视频结果对象的所有属性
                return Response({
                    "task_status": response.task_status,
                    "video_result": [
                        {
                            "url": video.url,
                            "cover_image_url": video.cover_image_url
                        } for video in response.video_result
                    ] if hasattr(response, 'video_result') else []
                }, status=status.HTTP_200_OK)
            else:
                # 生成视频
                # 获取参数
                model_name = request.data.get('model', 'cogvideox-flash')
                prompt = request.data.get('prompt')
                image_url = request.data.get('image_url')
                quality = request.data.get('quality', 'quality')
                with_audio = request.data.get('with_audio', True)
                size = request.data.get('size', '720x480')
                fps = request.data.get('fps', 30)
                
                # 基本验证
                if not prompt:
                    return Response({"error": "prompt is required"}, status=status.HTTP_400_BAD_REQUEST)
                
                # 生成视频
                response = client.videos.generations(
                    model=model_name,
                    prompt=prompt,
                    image_url=image_url,
                    quality=quality,
                    with_audio=with_audio,
                    size=size,
                    fps=fps
                )
                return Response({"task_id": response.id}, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
# GLM语音对话模型GLM-4-Voice
class GLM4Voice(APIView):
    def post(self, request):
        """生成语音请求"""
        try:
            # 初始化智谱AI客户端
            client = ZhipuAI(api_key=config.GLM_API_KEY)
            
            # 获取参数
            model_name = request.data.get('model', 'glm-4-voice')
            messages = request.data.get('messages', [])
            do_sample = request.data.get('do_sample', True)
            stream = request.data.get('stream', False)
            temperature = request.data.get('temperature', 0.8)
            top_p = request.data.get('top_p', 0.6)
            max_tokens = request.data.get('max_tokens', 1024)
            stop = request.data.get('stop')
            user_id = request.data.get('user_id')
            request_id = request.data.get('request_id')
            
            # 基本验证
            if not messages:
                return Response({"error": "messages is required"}, status=status.HTTP_400_BAD_REQUEST)
            
            # 调用API
            kwargs = {
                "model": model_name,
                "messages": messages,
                "do_sample": do_sample,
                "stream": stream,
                "temperature": temperature,
                "top_p": top_p,
                "max_tokens": max_tokens
            }
            
            # 添加可选参数
            if stop:
                kwargs["stop"] = stop
            if user_id:
                kwargs["user_id"] = user_id
            if request_id:
                kwargs["request_id"] = request_id
            
            response = client.chat.completions.create(**kwargs)
            
            # 构造响应
            result = {
                "id": response.id,
                "created": response.created,
                "model": response.model,
                "choices": [{
                    "index": choice.index,
                    "finish_reason": choice.finish_reason,
                    "message": {
                        "role": choice.message.role,
                        "content": choice.message.content,
                    }
                } for choice in response.choices],
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
            
            # 如果有音频数据，添加到结果中
            if hasattr(response.choices[0].message, "audio"):
                result["choices"][0]["message"]["audio"] = response.choices[0].message.audio
            
            return Response(result, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

# COZE对话模型
class CozeChatView(APIView):
    def post(self, request):
        """生成对话请求"""
        try:
            # 获取参数，api_token和bot_id使用默认配置值，但user_id必须由前端提供
            coze_api_token = request.data.get('api_token', config.COZE_API_TOKEN)
            bot_id = request.data.get('bot_id', config.COZE_BOT_ID)
            user_id = request.data.get('user_id')
            question = request.data.get('question')
            
            # 基本验证
            if not question:
                return Response({"error": "question is required"}, status=status.HTTP_400_BAD_REQUEST)
            if not user_id:
                return Response({"error": "user_id is required"}, status=status.HTTP_400_BAD_REQUEST)
            
            # 初始化Coze客户端
            coze = Coze(
                auth=TokenAuth(token=coze_api_token), 
                base_url=COZE_BASE_URL
            )
            
            content = ""
            token_count = 0
            
            # 使用stream方式调用API
            for event in coze.chat.stream(
                bot_id=bot_id,
                user_id=user_id,
                additional_messages=[
                    Message.build_user_question_text(question),
                ]
            ):
                # 实时处理消息增量
                if event.event == ChatEventType.CONVERSATION_MESSAGE_DELTA:
                    content += event.message.content
                
                # 完成时获取token用量
                if event.event == ChatEventType.CONVERSATION_CHAT_COMPLETED:
                    token_count = event.chat.usage.token_count
            
            # 构造响应
            result = {
                "content": content,
                "token_count": token_count
            }
            
            return Response(result, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

# Qwen模型
# 大语言模型-单轮对话
class QwenChat(APIView):
    def post(self, request):
        # 获取请求参数
        content = request.POST.get('content',  '')
        system_role = request.POST.get('system_role',  '用最温柔的语气回复我的问题')
        model = request.POST.get('model',  'qwen2.5-1.5b-instruct')  # 默认模型，可由前端指定
        
        # 构造消息列表
        messages = [
            {'role': 'system', 'content': system_role},
            {'role': 'user', 'content': content}
        ]
        
        try:
            # 调用 Generation.call  方法，关闭流式输出
            response = Generation.call( 
                api_key=config.QWEN_API_KEY,
                model=model,  # 使用前端传入的模型 
                messages=messages,
                result_format="message",
                stream=False  # 关闭流式输出
            )
            
            # 提取完整内容 
            full_content = ""
            if response.output  and response.output.choices: 
                for choice in response.output.choices: 
                    if choice.message  and choice.message.content: 
                        full_content += choice.message.content 
            
            # 返回完整结果
            return Response({'text': full_content})
        
        except Exception as e:
            # 捕获异常并返回错误信息
            return Response({'error': str(e)}, status=500)
# 视觉理解：
class Qwenvl(APIView):
    def post(self, request):
        try:
            # 获取请求数据
            data = request.data
            text = data.get('text', '')
            file_data = data.get('file')
            
            if not file_data:
                return Response({'error': '图片数据必填'}, status=400)
            
            client = OpenAI(
                api_key=config.QWEN_API_KEY,
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
            )
            
            # 记录请求信息
            logger.info(f"Qwenvl请求: text={text}")
            
            completion = client.chat.completions.create(
                model="qwen2-vl-2b-instruct",
                messages=[
                    {
                        "role": "system",
                        "content": [{"type": "text", "text": "你是一个专业的心理医生,需要结合用户提供的图片和问题,从心理和情绪的角度给出温暖的回应。"}]
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{file_data}"}
                            },
                            {"type": "text", "text": text or "请分析这张图片"}
                        ]
                    }
                ]
            )
            
            # 记录响应信息
            response_text = completion.choices[0].message.content
            logger.info(f"Qwenvl响应: {response_text}")
            
            return Response({'text': response_text})
            
        except Exception as e:
            logger.error(f"Qwenvl处理错误: {str(e)}\n{traceback.format_exc()}")
            return Response({'error': str(e)}, status=500)

# 大语言模型-长文本对话
class QwenChatFile(APIView):
    def post(self, request):
        try:
            # 获取上传的文件
            file = request.FILES.get('file')
            text = request.POST.get('text', '请分析这个文档')
            
            if not file:
                return Response({'error': '文件不能为空'}, status=400)
                
            # 记录请求信息
            logger.info(f"文件处理请求: filename={file.name}, text={text}")
            
            # 创建临时目录
            temp_dir = Path('temp_files')
            temp_dir.mkdir(exist_ok=True)
            
            # 保存文件
            file_path = temp_dir / file.name
            with open(file_path, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)
            
            try:
                # 初始化客户端
                client = OpenAI(
                    api_key=config.QWEN_API_KEY,
                    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
                )
                
                # 上传文件
                file_object = client.files.create(
                    file=file_path,
                    purpose="file-extract"
                )
                
                # 发送问题
                completion = client.chat.completions.create(
                    model="qwen-long",
                    messages=[
                        {"role": "system", "content": f"fileid://{file_object.id}"},
                        {"role": "user", "content": text}
                    ]
                )
                
                response_text = completion.choices[0].message.content
                # 记录响应信息
                logger.info(f"文件处理响应: {response_text}")
                
                return Response({'text': response_text})
                
            finally:
                # 清理文件
                if file_path.exists():
                    file_path.unlink()
                temp_dir.rmdir()
                
        except Exception as e:
            logger.error(f"文件处理错误: {str(e)}\n{traceback.format_exc()}")
            return Response({'error': str(e)}, status=500)
        
# 带应用Deeskeep版本
class deeskeep(APIView):
    def post(self, request):
        # 1. 从request.data获取内容更可靠，因为可以处理不同类型的请求
        content = request.data.get('content', '')
        session_id = request.session.get('session_id')
        has_thoughts = request.data.get('has_thoughts', True)  # 默认返回思考过程

        try:
            if not session_id:
                # 2. 添加错误处理
                if not config.QWEN_API_KEY or not config.QWEN_Deeskeep_ID:
                    return Response({'error': 'API配置缺失'}, status=500)
                
                # 初始化会话
                init_response = Application.call(
                    api_key=config.QWEN_API_KEY,
                    app_id=config.QWEN_Deeskeep_ID,
                    prompt=' '
                )
                
                # 3. 添加响应验证
                if not hasattr(init_response, 'output') or not hasattr(init_response.output, 'session_id'):
                    return Response({'error': '会话初始化失败'}, status=500)
                
                session_id = init_response.output.session_id
                request.session['session_id'] = session_id

            # 4. 添加输入验证
            if not content.strip():
                return Response({'error': '输入内容不能为空'}, status=400)

            # 调用API，使用用户输入和会话ID，添加has_thoughts参数
            response = Application.call(
                api_key=config.QWEN_API_KEY,
                app_id=config.QWEN_Deeskeep_ID,
                prompt=content,
                session_id=session_id,
                has_thoughts=has_thoughts  # 是否返回思考过程
            )
            
            # 检查状态码
            if response.status_code != 200:
                logger.error(f"API请求失败: request_id={response.request_id}, code={response.status_code}, message={response.message}")
                return Response({
                    'error': '模型请求失败',
                    'request_id': response.request_id,
                    'code': response.status_code,
                    'message': response.message
                }, status=500)
            
            # 构建返回结果
            result = {'text': response.output.text}
            
            # 如果包含思考过程，则添加到结果中
            if has_thoughts and hasattr(response.output, 'thoughts'):
                result['thoughts'] = response.output.thoughts
            
            return Response(result)
            
        except Exception as e:
            # 6. 添加日志记录
            logger.error(f"desskeep错误: {str(e)}", exc_info=True)
            return Response({'error': str(e)}, status=500)

# 大语言模型-多轮对话
class QwenChatToke(APIView):
    def post(self, request):
        # 1. 从request.data获取内容更可靠，因为可以处理不同类型的请求
        content = request.data.get('content', '')
        session_id = request.session.get('session_id')

        try:
            if not session_id:
                # 2. 添加错误处理
                if not config.QWEN_API_KEY or not config.QWEN_APP_ID:
                    return Response({'error': 'API配置缺失'}, status=500)
                
                # 初始化会话
                init_response = Application.call(
                    api_key=config.QWEN_API_KEY,
                    app_id=config.QWEN_APP_ID,
                    prompt=' '
                )
                
                # 3. 添加响应验证
                if not hasattr(init_response, 'output') or not hasattr(init_response.output, 'session_id'):
                    return Response({'error': '会话初始化失败'}, status=500)
                
                session_id = init_response.output.session_id
                request.session['session_id'] = session_id

            # 4. 添加输入验证
            if not content.strip():
                return Response({'error': '输入内容不能为空'}, status=400)

            # 调用API，使用用户输入和会话ID
            response = Application.call(
                api_key=config.QWEN_API_KEY,
                app_id=config.QWEN_APP_ID,
                prompt=content,
                session_id=session_id
            )
            
            # 5. 添加响应验证
            if not hasattr(response, 'output') or not hasattr(response.output, 'text'):
                return Response({'error': '无效的API响应'}, status=500)
                
            return Response({'text': response.output.text})
            
        except Exception as e:
            # 6. 添加日志记录
            logger.error(f"QwenChatToke错误: {str(e)}", exc_info=True)
            return Response({'error': str(e)}, status=500)
# 图像识别OCR
class QwenOCR(APIView):
    def post(self, request):
        try:
            client = OpenAI(
                api_key=config.QWEN_API_KEY,
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
            )
            uploaded_file = request.FILES.get('file')
            question = request.POST.get('question', '提取所有图中文字')
            if not uploaded_file:
                return JsonResponse({'error': '未上传文件'}, status=400)
            
            # 读取并编码文件
            file_data = base64.b64encode(uploaded_file.read()).decode('utf-8')
            
            completion = client.chat.completions.create(
                model="qwen-vl-ocr",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{file_data}"},
                                "min_pixels": 28 * 28 * 4,
                                "max_pixels": 28 * 28 * 1280
                            },
                            {"type": "text", "text": question},
                        ],
                    }
                ]
            )
            
            return JsonResponse({
                'response': completion.choices[0].message.content
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
# 多模态语音对话
class Qwenomni(APIView):
    def post(self, request):
        try:
            client = OpenAI(
                api_key=config.QWEN_API_KEY,
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
            )
            
            # 获取参数
            content_type = request.POST.get('type', 'text')  # text/image/audio/video
            text = request.POST.get('text', '')
            voice = request.POST.get('voice', config.DEFAULT_VOICE)
            url = request.POST.get('url', '')  # 获取URL参数
            
            # 获取对话历史
            messages = request.session.get('omni_dialog_history', [
                {
                    "role": "system",
                    "content": [{"type": "text", "text": "You are a helpful assistant."}]
                }
            ])
            
            # 构建消息内容
            if content_type == 'text':
                user_content = [{"type": "text", "text": text}]
            elif url:  # 处理URL方式
                if content_type == 'image':
                    user_content = [
                        {"type": "image_url", "image_url": {"url": url}},
                        {"type": "text", "text": text}
                    ]
                elif content_type == 'audio':
                    user_content = [
                        {"type": "input_audio", "input_audio": {"data": url, "format": "mp3"}},
                        {"type": "text", "text": text}
                    ]
                elif content_type == 'video':
                    user_content = [
                        {"type": "video_url", "video_url": {"url": url}},
                        {"type": "text", "text": text}
                    ]
            else:  # 处理文件上传方式
                file = request.FILES.get('file')
                if not file:
                    return JsonResponse({'error': '未上传文件'}, status=400)
                
                file_data = base64.b64encode(file.read()).decode('utf-8')
                
                if content_type == 'image':
                    user_content = [
                        {"type": "image_url", 
                         "image_url": {"url": f"data:image/jpeg;base64,{file_data}"}},
                        {"type": "text", "text": text}
                    ]
                elif content_type == 'audio':
                    user_content = [
                        {"type": "input_audio", 
                         "input_audio": {"data": f"data:;base64,{file_data}", "format": "mp3"}},
                        {"type": "text", "text": text}
                    ]
                elif content_type == 'video':
                    user_content = [
                        {"type": "video_url",
                         "video_url": {"url": f"data:;base64,{file_data}"}},
                        {"type": "text", "text": text}
                    ]
            
            # 添加用户消息到历史
            messages.append({"role": "user", "content": user_content})
            
            def stream_generator():
                completion = client.chat.completions.create(
                    model="qwen-omni-turbo",
                    messages=messages,
                    modalities=["text", "audio"],
                    audio={"voice": voice, "format": "wav"},
                    stream=True
                )
                
                assistant_response = []
                for chunk in completion:
                    if hasattr(chunk.choices[0].delta, "audio"):
                        try:
                            audio_data = chunk.choices[0].delta.audio['data']
                            assistant_response.append({"type": "audio", "audio": {"data": audio_data}})
                            yield f"audio:{audio_data}\n"
                        except Exception as e:
                            transcript = chunk.choices[0].delta.audio['transcript']
                            assistant_response.append({"type": "text", "text": transcript})
                            yield f"text:{transcript}\n"
                    elif hasattr(chunk.choices[0].delta, "content"):
                        content = chunk.choices[0].delta.content
                        if content:
                            assistant_response.append({"type": "text", "text": content})
                            yield f"text:{content}\n"
                
                # 添加助手回复到历史
                messages.append({"role": "assistant", "content": assistant_response})
                request.session['omni_dialog_history'] = messages
            
            return StreamingHttpResponse(stream_generator(), content_type='text/plain; charset=utf-8')
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

# Qwen 音频理解
class QwenAudio(APIView):
    def post(self, request):
        try:
            # 从Constance配置获取API密钥
            api_key = config.QWEN_API_KEY
            
            # 设置DashScope客户端
            dashscope.api_key = api_key
            
            # 获取音频文件
            file = request.FILES.get('file')
            if not file:
                logger.warning('未提供音频文件')
                return JsonResponse({'error': '未提供音频文件'}, status=400)
            
            # 记录文件信息
            logger.info(f'接收到音频文件: {file.name}, 大小: {file.size} bytes')
            
            # 检查文件大小
            if file.size > 10 * 1024 * 1024:  # 10MB
                logger.warning(f'文件过大: {file.size} bytes')
                return JsonResponse({'error': '音频文件不能超过10MB'}, status=400)
            
            try:
                # 读取并编码文件
                file_data = file.read()
                base64_audio = base64.b64encode(file_data).decode('utf-8')
                audio_source = f"data:audio/wav;base64,{base64_audio}"
                logger.info('音频文件编码成功')
                
                # 构造消息内容
                messages = [
                    {
                        "role": "system",
                        "content": [
                            {
                                "text": "用最温柔的口气回复我"
                            }
                        ]
                    },
                    {
                        "role": "user",
                        "content": [
                            {"audio": audio_source},
                            {"text": "用最温柔的口气回复我"}
                        ]
                    }
                ]
                
                # 调用通义千问音频理解模型
                logger.info('开始调用千问API')
                response = dashscope.MultiModalConversation.call(
                    model="qwen-audio-turbo-latest",
                    messages=messages,
                    stream=False,
                    result_format="message"
                )
                logger.debug(f'完整API响应: {json.dumps(response, default=lambda o: o.__dict__)}')
                
                # 处理响应
                if response.status_code == 200:
                    try:
                        # 增强响应结构解析
                        content = response.output.choices[0].message.content
                        
                        # 处理不同响应格式
                        if isinstance(content, list):
                            # 合并所有文本内容
                            texts = [item.get('text', '') for item in content if 'text' in item]
                            combined_text = '\n'.join(filter(None, texts))
                        elif isinstance(content, dict):
                            combined_text = content.get('text', '')
                        else:
                            combined_text = str(content)
                        
                        if combined_text:
                            logger.info(f'成功获取回复内容: {combined_text[:200]}...')  # 截断长文本
                            return JsonResponse({'text': combined_text})
                        
                        logger.warning('响应内容为空')
                        return JsonResponse({'error': '未获取到有效回复'}, status=500)
                        
                    except Exception as e:
                        logger.error(f'解析响应失败: {str(e)}\n{traceback.format_exc()}')
                        return JsonResponse({'error': '处理响应时发生错误'}, status=500)
                else:
                    logger.error(f'千问API返回错误: {response.code} - {response.message}')
                    return JsonResponse({
                        'error': '音频处理服务暂时不可用',
                        'detail': response.message
                    }, status=503)
                
            except IOError as e:
                logger.error(f'文件处理错误: {str(e)}')
                return JsonResponse({'error': '文件读取失败'}, status=500)
            finally:
                file.close()  # 确保文件资源释放
                
        except Exception as e:
            logger.error(f'系统错误: {str(e)}\n{traceback.format_exc()}')
            return JsonResponse({'error': '服务器内部错误'}, status=500)

    @action(detail=False, methods=['get'])
    def test_audio_api(self, request):
        try:
            # 使用官方示例音频测试
            test_audio_url = "https://dashscope.oss-cn-beijing.aliyuncs.com/audios/welcome.mp3"
            
            messages = [{
                "role": "user",
                "content": [
                    {"audio": test_audio_url},
                    {"text": "这段音频在说什么?"}
                ]
            }]
            
            response = dashscope.MultiModalConversation.call(
                model="qwen-audio-turbo-latest",
                messages=messages,
                result_format="message"
            )
            
            return JsonResponse({
                'status': 'success',
                'response': response.output.choices[0].message.content[0].text
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
