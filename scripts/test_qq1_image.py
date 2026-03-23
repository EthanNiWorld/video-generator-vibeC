#!/usr/bin/env python3
"""
测试使用 qq1.jpg 进行图生视频生成
"""

import requests
import os

BASE_URL = 'http://127.0.0.1:5001'
TEST_USERNAME = 'user'
TEST_PASSWORD = 'user123'

def test_qq1_image():
    """测试使用 qq1.jpg 进行图生视频生成"""
    session = requests.Session()
    
    # 登录
    login_data = {
        'username': TEST_USERNAME,
        'password': TEST_PASSWORD
    }
    session.post(f'{BASE_URL}/login', data=login_data)
    
    # 测试使用 qq1.jpg 进行图生视频生成
    print("测试使用 qq1.jpg 进行图生视频生成...")
    
    with open('qq1.jpg', 'rb') as f:
        test_data = {
            'prompt': 'Transform this image into a video',
            'model': 'wan2.6-i2v',
            'duration': 5,
            'model_selection': 'single'
        }
        files = {
            'image': f
        }
        
        response = session.post(f'{BASE_URL}/generate', data=test_data, files=files)
        if response.status_code == 302:
            print("✅ 图生视频请求提交成功")
            print("正在生成视频，请等待...")
        else:
            print("❌ 图生视频请求提交失败")
            print(f"状态码: {response.status_code}")
            print(f"响应: {response.text}")

if __name__ == '__main__':
    test_qq1_image()