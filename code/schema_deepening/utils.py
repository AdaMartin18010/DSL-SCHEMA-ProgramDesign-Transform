"""
Schema深化模块通用工具函数

提供通用的工具函数和辅助方法
"""

from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta
import json
import re
from pathlib import Path

from .logger import logger


def validate_uuid(uuid_str: str) -> bool:
    """
    验证UUID格式
    
    Args:
        uuid_str: UUID字符串
        
    Returns:
        是否为有效UUID
    """
    uuid_pattern = re.compile(
        r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
        re.IGNORECASE
    )
    return bool(uuid_pattern.match(uuid_str))


def validate_email(email: str) -> bool:
    """
    验证邮箱格式
    
    Args:
        email: 邮箱地址
        
    Returns:
        是否为有效邮箱
    """
    email_pattern = re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )
    return bool(email_pattern.match(email))


def validate_datetime_format(dt_str: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> bool:
    """
    验证日期时间格式
    
    Args:
        dt_str: 日期时间字符串
        format_str: 格式字符串
        
    Returns:
        是否为有效格式
    """
    try:
        datetime.strptime(dt_str, format_str)
        return True
    except ValueError:
        return False


def parse_datetime(dt_str: str, formats: Optional[List[str]] = None) -> Optional[datetime]:
    """
    解析日期时间字符串（支持多种格式）
    
    Args:
        dt_str: 日期时间字符串
        formats: 格式列表，如果为None则使用默认格式
        
    Returns:
        解析后的datetime对象，失败返回None
    """
    if formats is None:
        formats = [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%dT%H:%M:%S.%f",
            "%Y-%m-%dT%H:%M:%S.%fZ",
            "%Y-%m-%d",
            "%Y/%m/%d %H:%M:%S",
            "%Y/%m/%d"
        ]
    
    for fmt in formats:
        try:
            return datetime.strptime(dt_str, fmt)
        except ValueError:
            continue
    
    logger.warning(f"无法解析日期时间字符串: {dt_str}")
    return None


def safe_json_loads(json_str: str, default: Any = None) -> Any:
    """
    安全地解析JSON字符串
    
    Args:
        json_str: JSON字符串
        default: 解析失败时的默认值
        
    Returns:
        解析后的对象或默认值
    """
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError) as e:
        logger.warning(f"JSON解析失败: {str(e)}")
        return default


def safe_json_dumps(obj: Any, default: str = "{}") -> str:
    """
    安全地序列化对象为JSON字符串
    
    Args:
        obj: 要序列化的对象
        default: 序列化失败时的默认值
        
    Returns:
        JSON字符串或默认值
    """
    try:
        return json.dumps(obj, ensure_ascii=False, default=str)
    except (TypeError, ValueError) as e:
        logger.warning(f"JSON序列化失败: {str(e)}")
        return default


def normalize_path(path: Union[str, Path]) -> Path:
    """
    规范化路径
    
    Args:
        path: 路径字符串或Path对象
        
    Returns:
        规范化的Path对象
    """
    if isinstance(path, str):
        return Path(path).resolve()
    return path.resolve()


def ensure_directory(path: Union[str, Path]) -> Path:
    """
    确保目录存在，如果不存在则创建
    
    Args:
        path: 目录路径
        
    Returns:
        Path对象
    """
    dir_path = normalize_path(path)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path


def format_file_size(size_bytes: int) -> str:
    """
    格式化文件大小
    
    Args:
        size_bytes: 字节数
        
    Returns:
        格式化后的字符串
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"


def truncate_string(s: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    截断字符串
    
    Args:
        s: 原始字符串
        max_length: 最大长度
        suffix: 截断后的后缀
        
    Returns:
        截断后的字符串
    """
    if len(s) <= max_length:
        return s
    return s[:max_length - len(suffix)] + suffix


def deep_merge_dict(dict1: Dict, dict2: Dict) -> Dict:
    """
    深度合并字典
    
    Args:
        dict1: 第一个字典
        dict2: 第二个字典
        
    Returns:
        合并后的字典
    """
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge_dict(result[key], value)
        else:
            result[key] = value
    
    return result


def get_nested_value(data: Dict, path: str, default: Any = None, separator: str = ".") -> Any:
    """
    获取嵌套字典的值
    
    Args:
        data: 字典数据
        path: 路径，使用分隔符分隔
        default: 默认值
        separator: 路径分隔符
        
    Returns:
        值或默认值
    """
    keys = path.split(separator)
    current = data
    
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    
    return current


def set_nested_value(data: Dict, path: str, value: Any, separator: str = ".") -> None:
    """
    设置嵌套字典的值
    
    Args:
        data: 字典数据
        path: 路径，使用分隔符分隔
        value: 要设置的值
        separator: 路径分隔符
    """
    keys = path.split(separator)
    current = data
    
    for key in keys[:-1]:
        if key not in current:
            current[key] = {}
        current = current[key]
    
    current[keys[-1]] = value


def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """
    将列表分块
    
    Args:
        lst: 原始列表
        chunk_size: 每块的大小
        
    Returns:
        分块后的列表
    """
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def remove_none_values(data: Dict) -> Dict:
    """
    移除字典中的None值
    
    Args:
        data: 原始字典
        
    Returns:
        清理后的字典
    """
    return {k: v for k, v in data.items() if v is not None}


def calculate_percentage(part: float, total: float, precision: int = 2) -> float:
    """
    计算百分比
    
    Args:
        part: 部分值
        total: 总值
        precision: 精度
        
    Returns:
        百分比值
    """
    if total == 0:
        return 0.0
    return round((part / total) * 100, precision)


def generate_id(prefix: str = "id", timestamp: bool = True) -> str:
    """
    生成唯一ID
    
    Args:
        prefix: ID前缀
        timestamp: 是否包含时间戳
        
    Returns:
        生成的ID
    """
    if timestamp:
        return f"{prefix}_{datetime.utcnow().timestamp()}"
    else:
        import uuid
        return f"{prefix}_{uuid.uuid4().hex[:8]}"


def is_valid_url(url: str) -> bool:
    """
    验证URL格式
    
    Args:
        url: URL字符串
        
    Returns:
        是否为有效URL
    """
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return bool(url_pattern.match(url))
