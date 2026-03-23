#!/usr/bin/env python3
"""
测试OSS图片上传功能
"""

import os
import tempfile
from src.routes import upload_image_to_oss

# 创建临时测试图片
def create_test_image():
    # 创建一个简单的测试图片
    from PIL import Image
    import io
    
    # 创建一个200x200的红色图片
    img = Image.new('RGB', (200, 200), color='red')
    
    # 保存到临时文件
    temp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
    img.save(temp_file, format='JPEG')
    temp_file.close()
    
    return temp_file.name

def main():
    print("Testing OSS image upload...")
    
    # 创建测试图片
    test_image_path = create_test_image()
    print(f"Created test image: {test_image_path}")
    
    # 上传到OSS
    oss_url = upload_image_to_oss(test_image_path)
    
    if oss_url:
        print(f"✅ Upload successful! OSS URL: {oss_url}")
    else:
        print("❌ Upload failed!")
    
    # 清理临时文件
    os.unlink(test_image_path)
    print(f"Cleaned up test image: {test_image_path}")

if __name__ == "__main__":
    main()