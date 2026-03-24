#!/usr/bin/env python3
"""
测试豆包图生视频API调用
"""

import os
import requests
import json
import time
from http import HTTPStatus

# 豆包API配置
import os
API_KEY = os.getenv('VOLCENGINE_API_KEY', '')
API_URL = os.getenv('VOLCENGINE_API_URL', 'https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks')

# 测试用图片URL（使用真实存在的图片）
TEST_IMAGE_URL = 'https://ark-project.tos-cn-beijing.volces.com/doc_image/seepro_i2v.png'

# 测试参数
PROMPT = '无人机以极快速度穿越复杂障碍或自然奇观，带来沉浸式飞行体验'
DURATION = 5

# 构建请求体
def create_task():
    print("=== 创建豆包图生视频任务 ===")
    
    input_data = [
        {
            "type": "text",
            "text": f"{PROMPT} --duration {DURATION} --camerafixed false --watermark true"
        },
        {
            "type": "image_url",
            "image_url": {
                "url": TEST_IMAGE_URL
            }
        }
    ]
    
    payload = {
        "model": "doubao-seedance-1-5-pro-251215",
        "content": input_data
    }
    
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }
    
    print(f"API URL: {API_URL}")
    print(f"Headers: {headers}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        print(f"\n任务创建响应: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == HTTPStatus.OK:
            data = response.json()
            task_id = data.get('id')
            task_status = data.get('status', 'PENDING')
            print(f"\n任务ID: {task_id}")
            print(f"任务状态: {task_status}")
            return task_id, task_status
        else:
            print(f"任务创建失败: {response.status_code}")
            return None, None
    except Exception as e:
        print(f"错误: {str(e)}")
        return None, None

# 轮询任务状态
def poll_task(task_id):
    if not task_id:
        return None
    
    print("\n=== 轮询任务状态 ===")
    task_url = f"{API_URL}/{task_id}"
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }
    
    max_retries = 60  # 最多轮询60次，每次间隔5秒
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            response = requests.get(task_url, headers=headers, timeout=30)
            if response.status_code == HTTPStatus.OK:
                task_data = response.json()
                task_status = task_data.get('status')
                print(f"任务状态: {task_status}")
                
                if task_status == 'succeeded':
                    print(f"任务成功响应: {json.dumps(task_data, indent=2)}")
                    video_url = task_data.get('content', {}).get('video_url')
                    print(f"视频URL: {video_url}")
                    return video_url
                elif task_status == 'failed':
                    error_code = task_data.get('error', {}).get('code', 'Unknown')
                    error_message = task_data.get('error', {}).get('message', 'Unknown error')
                    print(f"任务失败: {error_code} - {error_message}")
                    return None
                elif task_status in ['pending', 'running', 'queued']:
                    print(f"任务处理中，等待5秒...")
                    time.sleep(5)
                    retry_count += 1
                else:
                    print(f"未知任务状态: {task_status}")
                    return None
            else:
                print(f"获取任务状态失败: {response.status_code}")
                time.sleep(5)
                retry_count += 1
        except Exception as e:
            print(f"错误: {str(e)}")
            time.sleep(5)
            retry_count += 1
    
    print("轮询超时")
    return None

# 下载视频
def download_video(video_url, filename):
    if not video_url:
        return False
    
    print("\n=== 下载视频 ===")
    try:
        response = requests.get(video_url, timeout=120)
        if response.status_code == HTTPStatus.OK:
            with open(filename, "wb") as f:
                f.write(response.content)
            print(f"视频下载成功: {filename}")
            return True
        else:
            print(f"视频下载失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"错误: {str(e)}")
        return False

# 主测试函数
def main():
    print("开始测试豆包图生视频API...")
    
    # 创建任务
    task_id, task_status = create_task()
    if not task_id:
        print("测试失败: 任务创建失败")
        return
    
    # 轮询任务状态
    video_url = poll_task(task_id)
    if not video_url:
        print("测试失败: 任务执行失败")
        return
    
    # 下载视频
    video_filename = f"doubao_test_video.mp4"
    success = download_video(video_url, video_filename)
    if success:
        print("\n🎉 测试成功！")
        print(f"视频已保存为: {video_filename}")
    else:
        print("测试失败: 视频下载失败")

if __name__ == "__main__":
    main()