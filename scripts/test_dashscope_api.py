#!/usr/bin/env python3
"""
测试DashScope API调用
"""

import os
import dashscope

# 设置API Key（使用新的API Key）
api_key = os.getenv('DASHSCOPE_API_KEY', 'sk-23151be2c4fe4eeb90fbd698cbe1d40d')
# 准备消息
messages = [
    {'role': 'system', 'content': 'You are a helpful assistant.'},
    {'role': 'user', 'content': '你是谁？'}
]

# 调用API
try:
    print("Calling DashScope API...")
    response = dashscope.Generation.call(
        api_key=api_key,
        model="qwen-plus",
        messages=messages,
        result_format='message'
    )
    print("API response:")
    print(response)
    
    # 提取并打印回答
    if hasattr(response, 'output') and hasattr(response.output, 'choices'):
        for choice in response.output.choices:
            if hasattr(choice, 'message') and hasattr(choice.message, 'content'):
                print("\nAssistant's answer:")
                print(choice.message.content)
except Exception as e:
    print(f"Error: {str(e)}")
