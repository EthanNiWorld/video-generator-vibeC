# Video Generator

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/flask-2.0%2B-green)](https://flask.palletsprojects.com/)

一个基于Flask的视频生成应用，支持多种AI视频生成模型。

## 功能特性

- 🎥 支持多种AI视频生成模型（wan系列、豆包系列等）
- 🖼️ 支持图生视频和文生视频
- 🔒 用户认证系统
- 📁 视频历史记录管理
- 📊 多模型并行生成

## 快速开始

### 安装

1. 克隆仓库
   ```bash
   git clone https://github.com/yourusername/video-generator.git
   cd video-generator
   ```

2. 创建虚拟环境
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # 在Windows上使用 venv\Scripts\activate
   ```

3. 安装依赖
   ```bash
   pip install -r requirements.txt
   ```

4. 配置环境变量
   创建 `.env` 文件并添加以下内容：
   ```
   # API Keys
   DASHSCOPE_API_KEY_WAN=your_wan_api_key
   DASHSCOPE_API_KEY_OTHER=your_other_api_key
   VOLCENGINE_API_KEY=your_volcengine_api_key
   
   # Database
   SQLALCHEMY_DATABASE_URI=sqlite:///site.db
   
   # Secret Key
   SECRET_KEY=your_secret_key
   ```

5. 启动应用
   ```bash
   python run.py
   ```

6. 访问应用
   打开浏览器访问 `http://127.0.0.1:5001`

## 许可证

本项目采用MIT许可证 - 详情请参阅 [LICENSE](LICENSE) 文件