#!/usr/bin/env python3
"""
使用qwen-plus模型翻译PO文件
"""

import os
import re
import json
import dashscope

# 设置API Key
api_key = os.getenv('DASHSCOPE_API_KEY', '')

# 读取messages.pot文件
def read_pot_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取所有需要翻译的字符串
    messages = []
    pattern = r'#:.*?msgid "(.*?)"\nmsgstr ""' 
    matches = re.findall(pattern, content, re.DOTALL)
    
    for match in matches:
        # 处理多行字符串
        message = match.replace('\n', ' ').strip()
        if message:
            messages.append(message)
    
    return messages

# 调用qwen-plus模型进行翻译
def translate_text(text, target_language):
    messages = [
        {'role': 'system', 'content': f'You are a professional translator. Translate the following text to {target_language}.'},
        {'role': 'user', 'content': text}
    ]
    
    response = dashscope.Generation.call(
        api_key=api_key,
        model="qwen-plus",
        messages=messages,
        result_format='message'
    )
    
    if hasattr(response, 'output') and hasattr(response.output, 'choices'):
        for choice in response.output.choices:
            if hasattr(choice, 'message') and hasattr(choice.message, 'content'):
                return choice.message.content.strip()
    
    return text

# 翻译并更新PO文件
def update_po_file(pot_file, po_file, target_language):
    # 读取pot文件
    messages = read_pot_file(pot_file)
    
    # 读取现有po文件
    with open(po_file, 'r', encoding='utf-8') as f:
        po_content = f.read()
    
    # 翻译并更新
    for message in messages:
        # 翻译
        translated = translate_text(message, target_language)
        print(f"Translating: {message} -> {translated}")
        
        # 更新po文件
        pattern = f'msgid "{re.escape(message)}"\nmsgstr ""'
        replacement = f'msgid "{message}"\nmsgstr "{translated}"'
        po_content = re.sub(pattern, replacement, po_content, flags=re.DOTALL)
    
    # 写入更新后的po文件
    with open(po_file, 'w', encoding='utf-8') as f:
        f.write(po_content)

# 主函数
def main():
    pot_file = 'messages.pot'
    
    # 翻译中文
    zh_po_file = 'translations/zh/LC_MESSAGES/messages.po'
    print("Translating to Chinese...")
    update_po_file(pot_file, zh_po_file, 'Chinese')
    
    # 翻译粤语
    yue_po_file = 'translations/yue/LC_MESSAGES/messages.po'
    print("\nTranslating to Cantonese...")
    update_po_file(pot_file, yue_po_file, 'Cantonese')
    
    # 编译翻译文件
    print("\nCompiling translation files...")
    os.system('source venv/bin/activate && pybabel compile -d translations')

if __name__ == "__main__":
    main()
