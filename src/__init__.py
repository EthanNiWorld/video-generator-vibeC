from flask import Flask, session
import os
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_babel import Babel

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Babel配置
app.config['BABEL_DEFAULT_LOCALE'] = 'zh'
app.config['BABEL_SUPPORTED_LOCALES'] = ['zh', 'en', 'yue']
app.config['BABEL_TRANSLATION_DIRECTORIES'] = os.path.join(os.path.dirname(__file__), '..', 'translations')

# 定义get_locale函数
def get_locale():
    # 从session中获取语言设置
    language = session.get('language')
    if language and language in app.config['BABEL_SUPPORTED_LOCALES']:
        return language
    # 如果没有设置语言，使用默认语言
    return app.config['BABEL_DEFAULT_LOCALE']

# 确保Babel正确初始化
babel = Babel(app, locale_selector=get_locale, default_domain='messages')

# 初始化扩展
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# 语言选择函数
def get_locale():
    from flask import request, session
    # 优先使用session中存储的语言
    if 'language' in session:
        return session['language']
    # 否则使用浏览器语言偏好
    return request.accept_languages.best_match(app.config['BABEL_SUPPORTED_LOCALES'])

# 初始化Babel
babel = Babel(app, locale_selector=get_locale)

# 注册get_locale函数到模板环境
app.jinja_env.globals['get_locale'] = get_locale

from src import models, routes

# 创建数据库表结构
with app.app_context():
    db.create_all()
