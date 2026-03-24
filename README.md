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
- 📡 实时进度显示
- 🌐 响应式设计

## 快速开始

### 安装

1. 克隆仓库
   ```bash
   git clone https://github.com/EthanNiWorld/video-generator-vibeCoding.git
   cd video-generator-vibeCoding
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
   - 复制 `.env.example` 文件为 `.env`
   ```bash
   cp .env.example .env
   ```
   - 编辑 `.env` 文件，添加真实的API密钥：
   ```
   # API Keys
   DASHSCOPE_API_KEY_WAN=your_wan_api_key_here
   DASHSCOPE_API_KEY_OTHER=your_other_api_key_here
   VOLCENGINE_API_KEY=your_volcengine_api_key_here
   
   # VolcEngine API URL
   VOLCENGINE_API_URL=https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks
   
   # VolcEngine Model Name
   VOLCENGINE_MODEL_NAME=doubao-seedance-1-5-pro-251215
   ```

5. 启动应用
   ```bash
   python run.py
   ```

6. 访问应用
   打开浏览器访问 `http://127.0.0.1:5001`

## 环境变量说明

| 环境变量 | 描述 | 示例值 |
|---------|------|--------|
| DASHSCOPE_API_KEY_WAN | 阿里云DashScope WAN模型API密钥 | sk-xxxxxxxxxxxxxxxx |
| DASHSCOPE_API_KEY_OTHER | 阿里云DashScope其他模型API密钥 | sk-xxxxxxxxxxxxxxxx |
| VOLCENGINE_API_KEY | 火山引擎API密钥 | your_volcengine_api_key_here |
| VOLCENGINE_API_URL | 火山引擎API URL | https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks |
| VOLCENGINE_MODEL_NAME | 火山引擎模型名称 | doubao-seedance-1-5-pro-251215 |

## 依赖管理

本项目使用 `requirements.txt` 文件管理依赖。如果需要添加新的依赖，可以运行：

```bash
pip install new-package
pip freeze > requirements.txt
```

## 常见问题

1. **端口被占用**
   - 错误信息：`Address already in use`
   - 解决方案：停止占用端口的进程或修改 `run.py` 中的端口号

2. **API密钥错误**
   - 错误信息：`Invalid API key`
   - 解决方案：检查 `.env` 文件中的API密钥是否正确

3. **视频生成失败**
   - 错误信息：`Task failed`
   - 解决方案：检查网络连接、API密钥权限或模型参数设置

## 许可证

本项目采用MIT许可证 - 详情请参阅 [LICENSE](LICENSE) 文件