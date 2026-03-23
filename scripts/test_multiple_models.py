#!/usr/bin/env python3
"""
测试多模型模式下的图生视频生成
"""

import requests
import os

BASE_URL = 'http://127.0.0.1:5001'
TEST_USERNAME = 'user'
TEST_PASSWORD = 'user123'

def test_multiple_models():
    """测试多模型模式下的图生视频生成"""
    session = requests.Session()
    
    # 登录
    login_data = {
        'username': TEST_USERNAME,
        'password': TEST_PASSWORD
    }
    session.post(f'{BASE_URL}/login', data=login_data)
    
    # 测试多模型模式，包含图生视频模型
    print("测试多模型模式，包含图生视频模型...")
    
    with open('qq1.jpg', 'rb') as f:
        test_data = {
            'prompt': 'Transform this image into a video',
            'model': 'wan2.6-t2v',  # 单模型默认值，多模型时会忽略
            'duration': 5,
            'model_selection': 'multiple',
            'multiple_models': ['wan2.6-i2v', 'wan2.6-t2v']  # 包含图生视频和文生视频模型
        }
        files = {
            'image': f
        }
        
        response = session.post(f'{BASE_URL}/generate', data=test_data, files=files)
        if response.status_code == 302:
            print("✅ 多模型请求提交成功")
            print("正在生成视频，请等待...")
        else:
            print("❌ 多模型请求提交失败")
            print(f"状态码: {response.status_code}")
            print(f"响应: {response.text}")

if __name__ == '__main__':
    test_multiple_models()