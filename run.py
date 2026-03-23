from src import app, db
from src.models import User, Video

if __name__ == '__main__':
    # 创建数据库表
    with app.app_context():
        db.create_all()
    # 启动应用
    app.run(debug=True, port=5001)
