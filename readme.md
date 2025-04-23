# 项目目录
此项目是后台的页面，首先需要安装requirements.txt的环境，然后修改settings.py文件，最后运行项目。具体参考下面步骤，下面步骤是我一步一步一步步的记录的，所以可以参考。
ai_app：是各大平台接口的内容，其中接口内容都卸载了views.py里面，所以需要自己删改，url.py是项目路由也是对外接口内容，admin.py和models.py是后台管理页面的内容

config：是项目配置文件，包括settings.py、urls.py、wsgi.py、asgi.py
emo_api:是关于心里评估量表的后台内容，其中views.py里面是各种量表的算法
wechat_app：是微信小程序相关的内容，主要就是前台的小程序基本就是个页面，后台来计算所有的东西，包括聊天，调用各大接口，还有心理评估量表的页面


# ========== 0. 项目目录 ==========
ssh打开虚拟环境的命令source py-project-env EMO_API

方法：
# ========== 1. 初始化Django项目 ==========
django-admin startproject config .

# ========== 2. 创建RDF应用 ==========
python3 manage.py startapp ai_app

# ========== 3. 安装依赖 ==========
pip install django python3-decouple mysqlclient pymysql
pip freeze > requirements.txt

# ========== 4. 数据库迁移 ==========
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser #超级管理员
python manage.py runserver

# ========== 5. 启动验证 ==========
python3 manage.py runserver

# ========== 6. 设置settings.py和urls.py ==========
设置ettings.py
LANGUAGE_CODE = 'zh-Hans'
TIME_ZONE = 'Asia/Shanghai'
INSTALLED_APPS = ['rest_framework','ai_app']

ALLOWED_HOSTS = [ ]#填写自己的域名，直接写域名不写http://

CSRF_TRUSTED_ORIGINS = [

DATABASES = {填写自己的数据库名称，用户名，密码，地址，端口}
CONSTANCE_CONFIG{根据自己需要配置的参数}
WECHAT_SITE_HOST = '填写自己的后台域名'

]#填写自己的域名http://开头
# ========== 7. AI相关路由和视图函数 ==========
主路由config/urls.py添加admin和ai_app里面的路由
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('ai_app.urls')),
]

创建ai_app/urls.py
先创建glm_4_flash路由（最基本的）
urlpatterns = [
    path('glm_4_flash/', glm_4_flash.as_view(), name='glm-4-flash'),
 ]

 创建ai_app/views.py
 具体参考代码即可，test.py是测试代码只测试glm_4_flash路由和返回的json格式
 # ========== 8. AI接口相关视图里面的注意 ==========
 0、..\EMO_API\ai_app\templates\api_docs.html是api文档页面，可以参考修改

 1、views.py里面的model是空的，需要手动传入，所以test.py是手动输入名称的，但是名称不能写错，没有校验机制

 2、glm模型名称包括（views.py）里面单独修改自己的api_key
    语言模型：
    glm-4-plus、glm-4-air、glm-4-air-0111、glm-4-airx、glm-4-long 、glm-4-flashx 、glm-4-flash；
    图/视频理解：
    glm-4v-plus-0111、glm-4v-plus 、glm-4v、glm-4v-flash；
    图像生成：
    cogview-4、cogview-3-flash、cogview-3；
    视频生成：
    cogvideox-2、cogvideox-flash；

3、coze参考CozeChatView；但这里最重要的就是access_token，需要30天更换一次；这个现在是卸载了传输段

4、qwen免费模型
    chat类
    qwen2.5-1.5b-instruct
    qwen-1.8b-longcontext-chat
    视觉类
    qwen2-vl-2b-instruct免费视觉
    功能类
    qwen2.5-math-1.5b-instruct数学解题
    qwen2.5-coder-3b-instruct代码变成，也可以使用更轻量级的1.5；0.5
    deepseek类
    deepseek-r1-distill-qwen-1.5b；deepseek-r1-distill-llama-8b；deepseek-r1-distill-llama-70b；
    wanx-ast图上加文字
    facechain-facedetect人物图像检测
    video-style-transform视频风格重绘：
    gte-rerank文本排序

 # ========== 9. 配置远程数据库 ==========
 1、数据库的安装配置：
    首先一定是8.0以上的mysql（我现在的操作系统是almalinux9.0）
    然后在宝塔里面安装mysql以及phpmyadmin,这两个设置的时候数据库要选择对所有人，phpmyadmin要白版选择安装
    如果不改动则MySQL会选择3306端口，phpmyadmin选择的是80端口
    一定要回到服务器里面去修改安全组，放行3306端口（Sys-WebServer安全组里面的出入方向都添加，TCP，3306，0.0.0.0/0）；多个数据库都是一样的3306端口
2、
 config/settings.py里面修改数据库
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': ' 写自己的数据库名称',
            'USER': ' 写自己的数据库用户名',
            'PASSWORD': ' 写自己的数据库密码',
            'HOST': ' 写自己的数据库地址',
            'PORT': '3306',
        }
    }
    同时下面的设置里面子应用要添加到INSTALLED_APPS里面，要不相对应的数据库不会迁移也不显示表

3.在app里面的models.py创建模型，然后迁移（所谓模型就是数据库的表）
    模型样例：
    class ModelInfo(models.Model):
        model = models.TextField()
        name = models.TextField()
        type = models.TextField()
        context = models.TextField()
        cost = models.TextField()
        def __str__(self):
            return f"{self.model} - {self.name} - {self.type} - {self.context} - {self.cost}"
    迁移：
    python3 manage.py makemigrations
    python3 manage.py migrate

4.在admin.py里面注册模型
    from django.contrib import admin
    from .models import ModelInfo
    admin.site.register(ModelInfo)

5.在apps.py里面注册应用并且显示中文
    name = 'ai_app'
    verbose_name = "AI-应用"

# ========== 10. 使用数据库案例 ==========
 1、把数据库导入到docs里面，先修改views.py增删改查的方法，增加models.py的内容，然后修改docs.html
 2、增删改查功能，则除了views.py里面添加了新的功能，同时urls.py里面和settings.py里面也要修改

# ========== 11. 搭建基础框架simpleui ==========
simpleui的配置：
1、安装依赖：pip install django-simpleui
2、添加应用：settings.py里面INSTALLED_APPS = ['simpleui',]
增加REST framework的视图及关系
3、手动添加serializers.py文件，文件内容参考文件，主要功能是序列化模型成为json格式
4、更新视图views.py，添加ModelInfoViewSet视图，用于管理模型信息；class ModelListView(APIView)，用于后台基础看框架
5、配置路由path('ModelListView/', ModelListView.as_view(),  name='ModelListView'),#framework视图

# ========== 12. 增加数据库表 ==========
1、在models.py里面增加新的模型，包括用户管理表、资源管理表、对话存储表
2、在admin.py里面注册模型,用@方式

# ========== 13. 动态配置参数管理django-constance ==========
1、pip install django-constance[database]
2、settings.py中添加：
    INSTALLED_APPS += ['constance']
    CONSTANCE_CONFIG = {
        'WECHAT_APP_ID': ('', '微信AppID'),
        'API_TIMEOUT': (30, '接口超时时间（秒）'),
    }
3、admin.py里面class CustomConstanceAdmin(ConstanceAdmin)是汉化用的，下面的是对站点标题汉化设置
4、对views.py里面的配置文件进行动态迁移

# ========== 14. 文件存储 ==========
1、安装依赖：pip install django-storages
   在views.py里面有上传接口，admin里面有“文件上传列表”
2、使用方法
    上传文件：
    POST /api/upload/
    Content-Type: multipart/form-data
    file: <文件数据>
    获取文件列表：
    GET /api/upload/
3、修改完迁移数据库和静态文件收集
    python3 manage.py makemigrations
    python3 manage.py migrate
    python3 manage.py collectstatic
4、media是上传文件的目录
5、static\admin\js\file_admin.js是上传页面的js文件，可以修改
6、staticfiles 文件夹说明：这是Django用来收集所有静态文件的目录
7、注意每此弄完了什么都要迁移数据库，迁移静态文件，迁移模型

# ========== 15. 微信管理wechat-django ==========
1、新建了wechat_app应用
    在views.py里面有微信支付的视图函数;具体的看其他的代码
    在urls.py里面有微信支付的路由
    在admin.py里面有微信支付的注册
    在models.py里面有微信支付的模型

2、垃圾微信必须要求https，这种恶心人所以本地开发的时候使用了花生壳这个奸商。和腾讯一样的垃圾
    1、下载花生壳把本地映射成为端口，把https复制出来到下一步
    2、一定在settints里面配置
    CSRF_TRUSTED_ORIGINS = ['上面给出来的地址', ]
    ALLOWED_HOSTS = ['上面给出来的地址',之前翻了个错误一直打不开admin其实是在地址最后面加了一个/小心这些小错误]
3、增加了微信小程序页面登录页面以及能否登录的开关，在admin中

# ========== 16. 微信小程序wechat_emo ==========
#### 微信app.js里面配置的apiBaseUrl是后台的地址，因为可能随时换，所以换最新的地址就行
1、在微信小程序的根目录下创建pages文件夹，然后在pages文件夹下创建ai文件夹，在ai文件夹下创建chat_emo文件夹
2、在chat_emo文件夹下创建chat_emo.js文件，chat_emo.wxml文件，chat_emo.wxss文件
3、class AppResource(models.Model)是资源库，可以存储图片、模型、API地址等资源，在models.py里面
4、class AppResourceAdmin(admin.ModelAdmin):是资源库的admin，在admin.py里面
5、连接资源库的方法在loadResources()，在chat_emo.js文件中。这里的后台地址必须要填写自己到时候替换，但是url是固定的path('resources/', views.get_resources, name='get_resources'),

# ========== 17. 心里评估量表 ==========
1、新建app的主要目的就是将量表，算法还有资源库整合在一起，方便管理
2、我在admin和models分别加了心理评估表的页面方法和数据库模型，还有用户测试记录的方法与模型。在上传评估表的时候一定要写清楚编号，这个编号涉及到之后有关的view里面的算法，因为没上传一个表就要做一个view，并且获取这个唯一对应的id。
3、用户id一定要从微信小程序获取，因为微信小程序的openid是唯一的，所以用户id就是openid。

 # ========== 18. 宝塔配置 ==========`
 1、正常上项目打包复制上去，在wwwroot里面，然后去“网站”去设置，新建项目，填写映射ssl证书这些的。点击运行不可以，必须点击终端，还有就是上华为把各种端口一键开放，主要是80和8000。
 2、启动的时候一定注意要在新建的网站里面点击终端，才会自动进入这个django的虚拟环境，然后打开这个终端pip install -r requirements.txt 安装依赖。（也可以在宝塔里用捅咕哦文件导入安装）
 3、除了这个虚拟环境，外面什么都没有，甚至python3版本管理都没有。日志也得进入到网页，从这个项目的设置里的选项看。
    需要pip的：pip install -r requirements.txt ；
    gunicorn;django；djangorestframework；django-constance；requests；zhipuai；cozepy；dashscope；openai；wechatpy；手动pip的mysqlclient；simpleui；
    需要安装的：sudo yum install mysql-devel 
    找到simpletags.py  文件把from django.utils.encoding  import force_text改成from django.utils.encoding  import smart_str as force_text

 4、然后运行python33 manage.py runserver，这个一定用3，不然会报错。
 5（可选检查）如果宝塔的配置里面location没有反向代理本地的话就把他添加上去：
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
9、运行python3 manage.py runserver