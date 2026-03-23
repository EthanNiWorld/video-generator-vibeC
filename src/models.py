from src import db
from flask_login import UserMixin
from datetime import datetime
import pytz

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    role = db.Column(db.String(10), nullable=False, default='user')  # user or admin
    last_used_date = db.Column(db.Date, nullable=True)
    usage_count = db.Column(db.Integer, default=0)
    videos = db.relationship('Video', backref='user', lazy=True)

# 获取北京时间
def get_beijing_time():
    return datetime.now(pytz.timezone('Asia/Shanghai'))

class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    prompt = db.Column(db.Text, nullable=False)
    video_path = db.Column(db.String(255), nullable=True)
    thumbnail_path = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=get_beijing_time)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class ErrorLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    error_message = db.Column(db.Text, nullable=False)
    error_type = db.Column(db.String(100), nullable=False)
    model = db.Column(db.String(100), nullable=True)
    prompt = db.Column(db.Text, nullable=True)
    api_request = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=get_beijing_time)
