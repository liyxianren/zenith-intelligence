import sys
import os

# 添加backend目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from flask import Flask
from app.config import config
from app.services.model_provider import model_provider_factory

# 创建Flask应用实例
app = Flask(__name__)
app.config.from_object(config['development'])

# 在应用上下文中测试
with app.app_context():
    print("Testing ChatGLM health check...")
    print(f"CHATGLM_API_KEY: {app.config.get('CHATGLM_API_KEY')}")
    print(f"CHATGLM_MODEL: {app.config.get('CHATGLM_MODEL')}")
    
    try:
        provider = model_provider_factory.get_provider("chatglm")
        health = provider.health_check()
        print(f"ChatGLM health check result: {health}")
    except Exception as e:
        print(f"Error: {e}")
