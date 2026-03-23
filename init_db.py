import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src import app, db

# 先导入db，再导入模型
print("Importing models...")
from src.models import User, Video, ErrorLog
print("Models imported successfully!")
print(f"User model: {User}")
print(f"Video model: {Video}")
print(f"ErrorLog model: {ErrorLog}")

# 创建数据库表结构
with app.app_context():
    print("\nCreating database tables...")
    try:
        # 先删除所有表（如果存在）
        db.drop_all()
        print("All existing tables dropped!")
        
        # 重新创建所有表
        db.create_all()
        print("Database tables created successfully!")
        
        # 检查表是否存在
        print("\nChecking tables...")
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"Tables in database: {tables}")
        
        # 检查video表的结构
        if 'video' in tables:
            print("\nVideo table columns:")
            columns = inspector.get_columns('video')
            for column in columns:
                print(f"  {column['name']}: {column['type']}")
        else:
            print("\nERROR: Video table does not exist!")
        
        # 创建测试用户
        print("\nCreating test users...")
        if User.query.filter_by(username='user').first() is None:
            user = User(username='user', email='user@example.com', password='user123', role='user')
            db.session.add(user)
            db.session.commit()
            print("Test user created successfully!")
        
        if User.query.filter_by(username='admin').first() is None:
            admin = User(username='admin', email='admin@example.com', password='admin123', role='admin')
            db.session.add(admin)
            db.session.commit()
            print("Admin user created successfully!")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
