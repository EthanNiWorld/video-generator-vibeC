from flask import render_template, url_for, flash, redirect, request, session
from flask_login import login_user, current_user, logout_user, login_required
from src import app, db, login_manager
from src.models import User, Video, ErrorLog
from datetime import datetime, date, timedelta
import os
import secrets
import requests
import json
import time
import pytz
import subprocess
from dotenv import load_dotenv
from http import HTTPStatus
import alibabacloud_oss_v2 as oss
from src.config import config
from src.error_handler import error_handler

# 加载环境变量
load_dotenv()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def upload_image_to_oss(image_path, bucket_name='ethan-ai-test', region='ap-southeast-1'):
    """上传图片到OSS并返回URL"""
    try:
        # 配置OSS客户端
        credentials_provider = oss.credentials.StaticCredentialsProvider(
            access_key_id=os.getenv('OSS_ACCESS_KEY_ID'),
            access_key_secret=os.getenv('OSS_ACCESS_KEY_SECRET')
        )
        
        cfg = oss.config.load_default()
        cfg.credentials_provider = credentials_provider
        cfg.region = region
        
        client = oss.Client(cfg)
        
        # 生成唯一的object key
        object_key = f"images/{secrets.token_hex(8)}_{os.path.basename(image_path)}"
        
        # 上传图片
        result = client.put_object_from_file(
            oss.PutObjectRequest(
                bucket=bucket_name,
                key=object_key
            ),
            image_path
        )
        
        # 生成OSS URL
        # 注意：这里使用公共读权限的URL格式，实际应用中可能需要根据OSS配置调整
        oss_url = f"https://{bucket_name}.oss-{region}.aliyuncs.com/{object_key}"
        
        print(f"Image uploaded to OSS: {oss_url}")
        print(f"Upload result: status code={result.status_code}, request id={result.request_id}")
        
        return oss_url
    except Exception as e:
        print(f"Error uploading image to OSS: {str(e)}")
        return None

@app.route('/')
@app.route('/home')
def home():
    if current_user.is_authenticated:
        # 获取筛选参数
        model_filter = request.args.get('model_filter', '')
        date_filter = request.args.get('date_filter', '')
        keyword_filter = request.args.get('keyword_filter', '')
        
        # 构建查询
        query = Video.query.filter_by(user_id=current_user.id)
        
        # 按模型筛选
        if model_filter:
            query = query.filter(Video.video_path.like(f'{model_filter}%'))
        
        # 按日期筛选
        if date_filter:
            try:
                filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
                # 筛选当天的视频
                query = query.filter(
                    db.func.date(Video.created_at) == filter_date
                )
            except ValueError:
                pass
        
        # 按关键词筛选
        if keyword_filter:
            query = query.filter(Video.prompt.contains(keyword_filter))
        
        # 按创建时间倒序排列
        user_videos = query.order_by(Video.created_at.desc()).all()
        
        return render_template('home.html', user_videos=user_videos)
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and password == user.password:  # 简化处理，实际应使用哈希
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

def generate_video_doubao(prompt, model, image_path=None, duration=10, image_url=None):
    """处理豆包和seedance系列模型的视频生成"""
    if model == 'seedance2.0':
        print(f"Seedance2.0 model selected, API integration pending")
        return None, None, None, None, True
    
    api_key = config.get_api_key(model)
    api_url = config.get_api_url(model)
    if not api_key:
        print("Error: VOLCENGINE_API_KEY environment variable is not set")
        return None, None, None, None, True
    print(f"Using Doubao endpoint for {model} model")
    
    input_data = []
    
    # 构建prompt，包含参数
    prompt_with_params = prompt
    prompt_with_params += f" --duration {duration}"
    prompt_with_params += " --camerafixed false"
    prompt_with_params += " --watermark true"
    
    input_data.append({
        "type": "text",
        "text": prompt_with_params
    })
    
    # 添加图片
    if image_url:
        input_data.append({
            "type": "image_url",
            "image_url": {
                "url": image_url
            }
        })
        print(f"Using provided image URL: {image_url}")
    elif image_path:
        # 上传图片到OSS
        oss_url = upload_image_to_oss(image_path)
        if oss_url:
            input_data.append({
                "type": "image_url",
                "image_url": {
                    "url": oss_url
                }
            })
            print(f"Using OSS image URL: {oss_url}")
        else:
            print("Failed to upload image to OSS")
            return None, None, None, None, True
    else:
        print("No image provided for doubao-seedance-1-5-pro model")
        return None, None, None, None, True
    
    # 构建请求体
    payload = {
        "model": config.VOLCENGINE_MODEL_NAME,
        "content": input_data
    }
    
    # 请求头部
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    return api_key, api_url, headers, payload, False

def generate_video_keling(prompt, model):
    """处理keling模型的视频生成"""
    print(f"Keling model selected, API integration pending")
    return None, None, None, None, True

def generate_video_aliyun(prompt, model='wan2.5-t2v-preview', image_path=None, duration=10, audio_url=None, negative_prompt=None, shot_type=None, image_url=None):
    """视频生成主函数"""
    # 实际调用视频生成API
    # 参考文档：https://bailian.console.aliyun.com/cn-beijing?tab=doc#/doc/?type=model&url=2873061
    
    # 初始化变量
    api_key = None
    api_url = None
    headers = None
    payload = None
    error = False
    
    # 根据模型类型处理
    if model in ['wan2.5-t2v-preview', 'wan2.6-t2v', 'wan2.6-t2v-flash', 'wan2.6-i2v']:
        # 处理wan系列模型
        api_key = config.get_api_key(model)
        api_url = config.get_api_url(model)
        print(f"Using Singapore endpoint for {model} model")
        
        # 请求参数
        input_data = {
            "prompt": prompt
        }
        
        # 如果是图生视频模型，添加图片URL
        if model == 'wan2.6-i2v':
            if image_url:
                # 使用提供的image_url
                input_data["img_url"] = image_url
                print(f"Using provided image URL: {image_url}")
            elif image_path:
                # 上传图片到OSS
                oss_url = upload_image_to_oss(image_path)
                if oss_url:
                    input_data["img_url"] = oss_url
                    print(f"Using OSS image URL: {oss_url}")
                else:
                    # 如果上传失败，返回错误
                    print("Failed to upload image to OSS")
                    return None, None, None, None, True
            else:
                # 没有提供图片，返回错误
                print("No image provided for wan2.6-i2v model")
                return None, None, None, None, True
        
        # 构建请求体
        payload = {
            "model": model,
            "input": input_data,
            "parameters": {
                "prompt_extend": False,  # 必须设置为False，否则无法生成NSFW内容
                "duration": duration,
                "watermark": config.DEFAULT_WATERMARK
            }
        }
        
        # 根据模型设置不同的尺寸
        if model == 'wan2.6-t2v' or model == 'wan2.6-t2v-flash':
            payload["parameters"]["size"] = "1280*720"
            # wan2.6系列支持shot_type
            if shot_type:
                payload["parameters"]["shot_type"] = shot_type
            # wan2.6系列支持audio_url
            if audio_url:
                input_data["audio_url"] = audio_url
        elif model == 'wan2.5-t2v-preview':
            payload["parameters"]["size"] = "832*480"
        elif model == 'wan2.6-i2v':
            payload["parameters"]["resolution"] = "720P"
        
        # 如果提供了负面提示词，添加到参数中
        if negative_prompt:
            input_data["negative_prompt"] = negative_prompt
        
        # 请求头部
        headers = {
            'X-DashScope-Async': 'enable',
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'X-DashScope-DataInspection': '{"input":"disable","output":"disable"}'
        }
    elif model in ['doubao-seedance-1-5-pro', 'seedance2.0']:
        # 处理豆包和seedance系列模型
        api_key, api_url, headers, payload, error = generate_video_doubao(
            prompt, model, image_path, duration, image_url
        )
    elif model == 'keling':
        # 处理keling模型
        api_key, api_url, headers, payload, error = generate_video_keling(prompt, model)
    else:
        print(f"Unknown model: {model}")
        return None, None, None, None
    
    # 检查是否有错误
    if error or not api_key:
        return None, None, None, None
    
    print("\n=== START OF API CALL ===")
    print(f"Calling API with prompt: {prompt}")
    print(f"Using model: {model}")
    print(f"Using API Key: {api_key}")
    print(f"API URL: {api_url}")
    print(f"Headers: {headers}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    task_id = None
    task_status = 'PENDING'
    
    try:
        # 创建任务
        print("Creating task...")
        response = requests.post(api_url, headers=headers, json=payload, timeout=30)
        print(f"Task created: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code != HTTPStatus.OK:
            print(f"Failed to create task: {response.status_code}")
            # 处理API错误
            error_handler.handle_api_error(
                response, 
                model, 
                prompt, 
                headers, 
                payload, 
                user_id=current_user.id if current_user.is_authenticated else None
            )
            return None, None, task_id, task_status
        
        # 解析响应
        data = response.json()
        if model == 'doubao-seedance-1-5-pro':
            task_id = data.get('id')
            task_status = data.get('status', 'PENDING')
        else:
            task_id = data.get('output', {}).get('task_id')
            task_status = data.get('output', {}).get('task_status', 'PENDING')
        print(f"Task ID: {task_id}")
        print(f"Task status: {task_status}")
        
        # 等待异步任务结束
        print("Waiting for task to complete...")
        if model == 'doubao-seedance-1-5-pro':
            task_url = f"https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks/{task_id}"
        else:
            task_url = f"https://dashscope-intl.aliyuncs.com/api/v1/tasks/{task_id}"
        task_headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        # 轮询任务状态
        max_retries = config.MAX_RETRIES  # 最多轮询60次，每次间隔5秒
        retry_count = 0
        while retry_count < max_retries:
            task_response = requests.get(task_url, headers=task_headers, timeout=30)
            if task_response.status_code == HTTPStatus.OK:
                task_data = task_response.json()
                if model == 'doubao-seedance-1-5-pro':
                    task_status = task_data.get('status')
                else:
                    task_status = task_data.get('output', {}).get('task_status')
                print(f"Task status: {task_status}")
                
                if task_status == 'SUCCEEDED' or task_status == 'succeeded':
                    if model == 'doubao-seedance-1-5-pro':
                        # 豆包API成功响应
                        video_url = task_data.get('content', {}).get('video_url')
                    else:
                        # 阿里云API成功响应
                        video_url = task_data.get('output', {}).get('video_url')
                    print(f"Video URL: {video_url}")
                    
                    # 下载视频
                    print("Downloading video...")
                    video_response = requests.get(video_url, timeout=120)
                    if video_response.status_code == HTTPStatus.OK:
                        # 生成视频文件名（包含模型前缀）
                        video_filename = f"{model}_video_{secrets.token_hex(8)}.mp4"
                        video_path = os.path.join('src/static/videos', video_filename)
                        
                        # 保存视频
                        with open(video_path, "wb") as f:
                            f.write(video_response.content)
                        print(f"Video downloaded successfully: {video_filename}")
                        
                        # 生成视频缩略图
                        thumbnail_filename = f"{model}_thumbnail_{secrets.token_hex(8)}.jpg"
                        thumbnail_path = os.path.join('src/static/videos', thumbnail_filename)
                        
                        try:
                            # 使用ffmpeg从视频中提取第一帧作为缩略图
                            subprocess.run([
                                'ffmpeg', '-i', video_path, '-ss', '00:00:01', '-vframes', '1',
                                '-s', '320x180', '-y', thumbnail_path
                            ], check=True, capture_output=True)
                            print(f"Thumbnail generated successfully: {thumbnail_filename}")
                        except subprocess.CalledProcessError as e:
                            print(f"Error generating thumbnail: {str(e)}")
                            thumbnail_filename = None
                        
                        # 保存测试记录
                        timestamp = time.strftime('%Y%m%d%H')
                        
                        # 确保tests目录存在
                        os.makedirs('tests', exist_ok=True)
                        report_filename = f"test_report_{timestamp}.txt"
                        report_path = os.path.join('tests', report_filename)
                        
                        # 写入测试报告
                        with open(report_path, "w") as f:
                            f.write("=== 测试报告 ===\n")
                            f.write(f"测试时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                            f.write(f"时间戳: {timestamp}\n")
                            f.write(f"API Key: {api_key}\n")
                            f.write(f"API URL: {api_url}\n")
                            f.write(f"Headers: {json.dumps(headers, indent=2)}\n")
                            f.write(f"Payload: {json.dumps(payload, indent=2)}\n")
                            f.write(f"Task ID: {task_id}\n")
                            f.write(f"Video URL: {video_url}\n")
                            f.write(f"Video Filename: {video_filename}\n")
                            f.write(f"Thumbnail Filename: {thumbnail_filename}\n")
                            f.write(f"Prompt: {prompt}\n")
                            f.write(f"Model: {model}\n")
                            f.write(f"Duration: {duration} seconds\n")
                            f.write(f"Task Status: SUCCEEDED\n")
                        
                        print(f"Test report generated: {report_path}")
                        return video_filename, thumbnail_filename, task_id, task_status
                elif task_status == 'FAILED' or task_status == 'failed':
                    # 记录失败的任务状态
                    print(f"Task failed with status: {task_status}")
                    # 处理任务错误
                    error_handler.handle_task_error(
                        task_data, 
                        model, 
                        prompt, 
                        headers, 
                        payload, 
                        user_id=current_user.id if current_user.is_authenticated else None
                    )
                    return None, None, task_id, task_status
                elif task_status in ['PENDING', 'RUNNING', 'pending', 'running']:
                    # 任务正在处理中，继续轮询
                    print(f"Task is {task_status}, waiting...")
                    time.sleep(config.RETRY_INTERVAL)
                    retry_count += 1
                else:
                    # 其他任务状态
                    print(f"Task status: {task_status}")
                    return None, None, task_id, task_status
            else:
                print(f"Failed to get task status: {task_response.status_code}")
                time.sleep(5)
                retry_count += 1
        
        # 轮询超时
        print("Task polling timeout")
        return None, None, task_id, task_status
        
    except Exception as e:
        print(f"Error: {str(e)}")
        # 记录错误
        error_handler.log_error(
            type(e).__name__, 
            str(e),
            model=model,
            prompt=prompt,
            user_id=current_user.id if current_user.is_authenticated else None
        )
        return None, None, task_id, task_status

@app.route('/generate', methods=['POST'])
@login_required
def generate():
    print("\n=== START OF GENERATE FUNCTION ===")
    
    # 打印请求信息
    print(f"Request method: {request.method}")
    print(f"Request form keys: {list(request.form.keys())}")
    print(f"Request files keys: {list(request.files.keys())}")
    
    prompt = request.form.get('prompt')
    model = request.form.get('model', 'wan2.5-t2v-preview')
    duration = int(request.form.get('duration', 10))
    audio_url = request.form.get('audio_url')
    negative_prompt = request.form.get('negative_prompt')
    shot_type = request.form.get('shot_type')
    
    # 取消使用次数限制
    print("Usage limit disabled")
    
    print(f"Prompt: {prompt}")
    print(f"Model: {model}")
    print(f"Duration: {duration} seconds")
    
    if not prompt:
        flash('Please enter a prompt', 'danger')
        print("No prompt provided")
        return redirect(url_for('home'))
    
    # 处理图片上传（如果是图生视频模型）
    image_path = None
    image_url = None
    
    # 检查是否需要图片
    model_selection = request.form.get('model_selection', 'single')
    requires_image = False
    
    if model_selection == 'single':
        if model == 'wan2.6-i2v' or model == 'doubao-seedance-1-5-pro':
            requires_image = True
    else:
        # 多模型选择
        multiple_models = request.form.getlist('multiple_models')
        for model_name in multiple_models:
            if model_name == 'wan2.6-i2v' or model_name == 'doubao-seedance-1-5-pro':
                requires_image = True
                break
    
    if requires_image:
        print("Processing image for image-to-video model")
        # 优先使用提供的image_url
        if 'image_url' in request.form and request.form['image_url']:
            image_url = request.form['image_url']
            print(f"Using provided image URL: {image_url}")
        elif 'image' in request.files and request.files['image'].filename != '':
            image = request.files['image']
            # 保存上传的图片
            image_filename = f"image_{secrets.token_hex(8)}.jpg"
            image_path = os.path.join('src/static/videos', image_filename)
            image.save(image_path)
            print(f"Image uploaded: {image_filename}")
            print(f"Image saved to: {image_path}")
        else:
            print("No image in request files and no image_url provided")
            flash('Please upload an image or provide an image URL for image-to-video generation', 'danger')
            return redirect(url_for('home'))
    
    # 处理多个模型测试
    multiple_models = request.form.getlist('multiple_models')
    
    # 存储任务信息
    task_info = []
    
    def process_model(model_name):
        """处理单个模型的视频生成"""
        print(f"Generating video with model: {model_name}")
        # 调用阿里云视频生成API
        video_filename, thumbnail_filename, task_id, task_status = generate_video_aliyun(
            prompt, model_name, image_path, duration, 
            audio_url=audio_url, negative_prompt=negative_prompt, 
            shot_type=shot_type, image_url=image_url
        )
        
        # 存储任务信息
        task_info.append({
            'model': model_name,
            'task_id': task_id,
            'status': task_status,
            'success': bool(video_filename)
        })
        
        if video_filename:
            print(f"Video generated successfully with {model_name}: {video_filename}")
            # 保存记录
            video = Video(prompt=prompt, video_path=video_filename, thumbnail_path=thumbnail_filename, user_id=current_user.id)
            db.session.add(video)
            return True
        else:
            print(f"Failed to generate video with {model_name}")
            return False
    
    if multiple_models:
        print(f"Testing multiple models: {multiple_models}")
        success_count = 0
        
        for model_name in multiple_models:
            if process_model(model_name):
                success_count += 1
        
        # 提交所有记录
        db.session.commit()
        
        if success_count > 0:
            flash(f'Videos generated successfully! {success_count} out of {len(multiple_models)} models completed.', 'success')
            print(f"Multiple models test completed: {success_count} out of {len(multiple_models)} models succeeded")
        else:
            flash('Failed to generate videos. Please try again later.', 'danger')
            print("All models failed to generate video")
    else:
        # 调用单个模型
        print("Calling generate_video_aliyun function")
        if not process_model(model):
            flash('Failed to generate video. Please try again later.', 'danger')
            return redirect(url_for('home'))
        
        # 提交记录
        db.session.commit()
        
        flash('Video generated successfully!', 'success')
        print("Video generated successfully")
    
    # 将任务信息存储到session中，以便在首页显示
    session['task_info'] = task_info
    
    print("=== END OF GENERATE FUNCTION ===")
    return redirect(url_for('home'))

@app.route('/admin')
@login_required
def admin():
    if current_user.role != 'admin':
        flash('You do not have access to this page', 'danger')
        return redirect(url_for('home'))
    
    # 获取分页参数
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # 获取视频记录（分页）
    videos_pagination = Video.query.order_by(Video.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    videos = videos_pagination.items
    
    # 统计数据
    total_videos = Video.query.count()
    
    # 按模型统计
    model_stats = {}
    all_videos = Video.query.all()
    for video in all_videos:
        if video.video_path:
            model_name = video.video_path.split('_')[0]
            if model_name not in model_stats:
                model_stats[model_name] = 0
            model_stats[model_name] += 1
    
    # 按用户统计
    user_stats = {}
    for video in all_videos:
        username = video.user.username
        if username not in user_stats:
            user_stats[username] = 0
        user_stats[username] += 1
    
    # 最近7天的视频生成趋势
    seven_days_ago = datetime.now(pytz.timezone('Asia/Shanghai')) - timedelta(days=7)
    daily_stats = {}
    for video in all_videos:
        # 确保 created_at 是带时区的
        if not video.created_at.tzinfo:
            # 如果不带时区，添加北京时间时区
            video.created_at = pytz.timezone('Asia/Shanghai').localize(video.created_at)
        if video.created_at >= seven_days_ago:
            date_str = video.created_at.strftime('%Y-%m-%d')
            if date_str not in daily_stats:
                daily_stats[date_str] = 0
            daily_stats[date_str] += 1
    
    # 排序日期
    sorted_dates = sorted(daily_stats.keys())
    daily_values = [daily_stats[date] for date in sorted_dates]
    
    # 获取错误日志（分页）
    error_page = request.args.get('error_page', 1, type=int)
    error_logs_pagination = ErrorLog.query.order_by(ErrorLog.created_at.desc()).paginate(page=error_page, per_page=per_page, error_out=False)
    error_logs = error_logs_pagination.items
    total_errors = ErrorLog.query.count()
    
    # 获取用户创建消息
    create_user_message = request.args.get('create_user_message')
    
    return render_template('admin.html', 
        videos=videos, 
        total_videos=total_videos, 
        model_stats=model_stats, 
        user_stats=user_stats, 
        sorted_dates=sorted_dates, 
        daily_values=daily_values, 
        error_logs=error_logs, 
        total_errors=total_errors, 
        create_user_message=create_user_message,
        videos_pagination=videos_pagination,
        error_logs_pagination=error_logs_pagination
    )

@app.route('/create_admin')
def create_admin():
    # 创建管理员账户，仅用于首次设置
    admin_user = User.query.filter_by(username='admin').first()
    if not admin_user:
        admin_user = User(username='admin', email='admin@example.com', password='admin123', role='admin')
        db.session.add(admin_user)
        db.session.commit()
    return 'Admin account created successfully!'

@app.route('/init_user')
def init_user():
    # 创建普通用户账户，仅用于首次设置
    user = User.query.filter_by(username='user').first()
    if not user:
        user = User(username='user', email='user@example.com', password='user123', role='user')
        db.session.add(user)
        db.session.commit()
    return 'User account created successfully!'

@app.route('/set_language', methods=['POST'])
def set_language():
    language = request.form.get('language')
    if language in ['zh', 'en', 'yue']:
        session['language'] = language
    # 重定向到当前页面，确保语言切换生效
    return redirect(request.referrer or url_for('home'))

@app.route('/about')
@login_required
def about():
    return render_template('about.html')

@app.route('/create_user', methods=['POST'])
@login_required
def create_user():
    if current_user.role != 'admin':
        flash('You do not have access to this page', 'danger')
        return redirect(url_for('home'))
    
    username = request.form.get('new_username')
    
    if not username:
        return redirect(url_for('admin'))
    
    # 检查用户是否已存在
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return redirect(url_for('admin', create_user_message=f'User {username} already exists (Status: Failed)'))
    
    # 创建新用户，密码为用户名加123，默认角色为user，邮箱使用默认格式
    password = f"{username}123"
    email = f"{username}@example.com"
    new_user = User(
        username=username,
        email=email,
        password=password,
        role="user"
    )
    db.session.add(new_user)
    db.session.commit()
    
    # 重定向回admin页面，并传递创建成功消息
    return redirect(url_for('admin', create_user_message=f'User {username} created successfully with password: {password} (Status: Success). Users can change their password after logging in.'))

@app.route('/clear_task_info')
@login_required
def clear_task_info():
    """清除session中的任务信息"""
    if 'task_info' in session:
        del session['task_info']
    return {"status": "success"}
