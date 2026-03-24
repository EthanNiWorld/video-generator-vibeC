import os
import sys
import socket
from src import app, db
from src.models import User, Video


def get_available_port(port):
    """获取可用端口"""
    while True:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        if result != 0:
            return port
        print(f"端口 {port} 已被占用，尝试使用端口 {port + 1}")
        port += 1


if __name__ == '__main__':
    # 获取端口号
    port = int(os.getenv('PORT', 5001))
    
    # 检查命令行参数
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print(f"无效的端口号: {sys.argv[1]}，使用默认端口 {port}")
    
    # 查找可用端口
    port = get_available_port(port)
    
    # 创建数据库表
    with app.app_context():
        db.create_all()
    
    # 启动应用
    print(f"启动应用，监听端口: {port}")
    app.run(debug=True, port=port)
