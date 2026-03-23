from src import db
from src.models import ErrorLog
import json

class ErrorHandler:
    """错误处理类"""
    
    @staticmethod
    def log_error(error_type, error_message, model=None, prompt=None, api_request=None, user_id=None):
        """记录错误到错误日志"""
        try:
            error_log = ErrorLog(
                error_type=error_type,
                error_message=error_message,
                model=model,
                prompt=prompt,
                api_request=api_request,
                user_id=user_id
            )
            db.session.add(error_log)
            db.session.commit()
            print(f"Error logged: {error_type} - {error_message}")
        except Exception as e:
            print(f"Failed to log error: {str(e)}")
    
    @staticmethod
    def handle_api_error(response, model, prompt, headers, payload, user_id=None):
        """处理API错误"""
        try:
            data = response.json()
            error_message = data.get('error', {}).get('message', 'Unknown error')
            error_code = data.get('error', {}).get('code', 'Unknown code')
            print(f"API Error - Code: {error_code}")
            print(f"API Error - Message: {error_message}")
            
            # 记录错误到错误日志
            api_request = json.dumps({"headers": headers, "payload": payload}, indent=2)
            ErrorHandler.log_error(
                "APIError", 
                f"API call failed: {response.status_code} - {error_message}",
                model=model,
                prompt=prompt,
                api_request=api_request,
                user_id=user_id
            )
            
            return error_message
        except Exception as e:
            print(f"Failed to handle API error: {str(e)}")
            return "Unknown API error"
    
    @staticmethod
    def handle_task_error(task_data, model, prompt, headers, payload, user_id=None):
        """处理任务错误"""
        try:
            if model == 'doubao-seedance-1-5-pro':
                # 豆包API失败响应
                error_code = task_data.get('error', {}).get('code', 'Unknown')
                error_message = task_data.get('error', {}).get('message', 'Unknown error')
            else:
                # 阿里云API失败响应
                error_code = task_data.get('output', {}).get('code', 'Unknown')
                error_message = task_data.get('output', {}).get('message', 'Unknown error')
            
            print(f"Task Error - Code: {error_code}")
            print(f"Task Error - Message: {error_message}")
            
            # 记录错误到错误日志
            api_request = json.dumps({"headers": headers, "payload": payload}, indent=2)
            ErrorHandler.log_error(
                "InvalidTask", 
                f"Task failed with code: {error_code}, message: {error_message}",
                model=model,
                prompt=prompt,
                api_request=api_request,
                user_id=user_id
            )
            
            return error_message
        except Exception as e:
            print(f"Failed to handle task error: {str(e)}")
            return "Unknown task error"

# 创建错误处理器实例
error_handler = ErrorHandler()