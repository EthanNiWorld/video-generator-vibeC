import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Config:
    """配置管理类"""
    
    # API密钥配置
    DASHSCOPE_API_KEY_WAN = os.getenv('DASHSCOPE_API_KEY_WAN')
    DASHSCOPE_API_KEY_OTHER = os.getenv('DASHSCOPE_API_KEY_OTHER')
    VOLCENGINE_API_KEY = os.getenv('VOLCENGINE_API_KEY')
    
    # API URL配置
    WAN_API_URL = 'https://dashscope-intl.aliyuncs.com/api/v1/services/aigc/video-generation/video-synthesis'
    OTHER_API_URL = 'https://dashscope.aliyuncs.com/api/v1/services/aigc/video-generation/video-synthesis'
    VOLCENGINE_API_URL = os.getenv('VOLCENGINE_API_URL', 'https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks')
    
    # 模型配置
    VOLCENGINE_MODEL_NAME = os.getenv('VOLCENGINE_MODEL_NAME', 'doubao-seedance-1-5-pro-251215')
    
    # 任务轮询配置
    MAX_RETRIES = 60
    RETRY_INTERVAL = 5
    
    # 图片配置
    PLACEHOLDER_IMAGE_URL = 'https://example.com/test_image.jpg'
    
    # 视频配置
    DEFAULT_DURATION = 10
    DEFAULT_WATERMARK = True
    
    # 响应状态码
    HTTP_OK = 200
    
    @staticmethod
    def get_api_key(model):
        """根据模型获取API密钥"""
        if model in ['wan2.5-t2v-preview', 'wan2.6-t2v', 'wan2.6-t2v-flash', 'wan2.6-i2v']:
            return Config.DASHSCOPE_API_KEY_WAN
        elif model == 'doubao-seedance-1-5-pro':
            return Config.VOLCENGINE_API_KEY
        else:
            return Config.DASHSCOPE_API_KEY_OTHER
    
    @staticmethod
    def get_api_url(model):
        """根据模型获取API URL"""
        if model in ['wan2.5-t2v-preview', 'wan2.6-t2v', 'wan2.6-t2v-flash', 'wan2.6-i2v']:
            return Config.WAN_API_URL
        elif model == 'doubao-seedance-1-5-pro':
            return Config.VOLCENGINE_API_URL
        else:
            return Config.OTHER_API_URL

# 创建配置实例
config = Config()