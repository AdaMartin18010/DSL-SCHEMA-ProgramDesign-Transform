"""
数据格式化模块

专注于数据格式化、格式转换、格式验证
"""

from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import re
import logging

logger = logging.getLogger(__name__)


class FormatType(Enum):
    """格式类型"""
    DATE = "date"  # 日期格式
    TIME = "time"  # 时间格式
    DATETIME = "datetime"  # 日期时间格式
    NUMBER = "number"  # 数字格式
    CURRENCY = "currency"  # 货币格式
    PERCENTAGE = "percentage"  # 百分比格式
    PHONE = "phone"  # 电话格式
    EMAIL = "email"  # 邮箱格式
    URL = "url"  # URL格式
    CUSTOM = "custom"  # 自定义格式


@dataclass
class FormatRule:
    """格式规则"""
    field: str
    format_type: FormatType
    target_format: str
    validation: bool = True


@dataclass
class FormatResult:
    """格式化结果"""
    format_id: str
    records_processed: int
    records_formatted: int
    format_time: float
    data: List[Dict[str, Any]]
    errors: List[Dict[str, Any]] = None


class DataFormatter:
    """
    数据格式化器
    
    专注于数据格式化、格式转换、格式验证
    """
    
    def __init__(self):
        self.format_history: List[FormatResult] = []
    
    def format_data(self, data: List[Dict[str, Any]], rules: List[FormatRule]) -> FormatResult:
        """
        格式化数据
        
        Args:
            data: 数据列表
            rules: 格式规则列表
            
        Returns:
            格式化结果
        """
        format_id = f"format_{datetime.utcnow().timestamp()}"
        start_time = datetime.utcnow()
        
        formatted_data = []
        records_formatted = 0
        errors = []
        
        for i, record in enumerate(data):
            formatted_record = record.copy()
            modified = False
            
            for rule in rules:
                if rule.field in formatted_record:
                    try:
                        original_value = formatted_record[rule.field]
                        formatted_value = self._apply_format(original_value, rule)
                        
                        if formatted_value != original_value:
                            formatted_record[rule.field] = formatted_value
                            modified = True
                    except Exception as e:
                        errors.append({
                            'record_index': i,
                            'field': rule.field,
                            'error': str(e)
                        })
            
            formatted_data.append(formatted_record)
            if modified:
                records_formatted += 1
        
        end_time = datetime.utcnow()
        format_time = (end_time - start_time).total_seconds()
        
        result = FormatResult(
            format_id=format_id,
            records_processed=len(data),
            records_formatted=records_formatted,
            format_time=format_time,
            data=formatted_data,
            errors=errors if errors else None
        )
        
        self.format_history.append(result)
        return result
    
    def _apply_format(self, value: Any, rule: FormatRule) -> Any:
        """应用格式"""
        if value is None:
            return value
        
        format_type = rule.format_type
        target_format = rule.target_format
        
        if format_type == FormatType.DATE:
            if isinstance(value, str):
                try:
                    dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
                    return dt.strftime(target_format)
                except:
                    return value
            return value
        
        elif format_type == FormatType.TIME:
            if isinstance(value, str):
                try:
                    dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
                    return dt.strftime(target_format)
                except:
                    return value
            return value
        
        elif format_type == FormatType.DATETIME:
            if isinstance(value, str):
                try:
                    dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
                    return dt.strftime(target_format)
                except:
                    return value
            return value
        
        elif format_type == FormatType.NUMBER:
            if isinstance(value, (int, float)):
                return format(value, target_format)
            return value
        
        elif format_type == FormatType.CURRENCY:
            if isinstance(value, (int, float)):
                currency_symbol = target_format or '$'
                return f"{currency_symbol}{value:,.2f}"
            return value
        
        elif format_type == FormatType.PERCENTAGE:
            if isinstance(value, (int, float)):
                return f"{value * 100:.2f}%"
            return value
        
        elif format_type == FormatType.PHONE:
            if isinstance(value, str):
                digits = re.sub(r'\D', '', value)
                if len(digits) == 10:
                    return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
                elif len(digits) == 11:
                    return f"{digits[0]} ({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
            return value
        
        elif format_type == FormatType.EMAIL:
            if isinstance(value, str):
                return value.lower().strip()
            return value
        
        elif format_type == FormatType.URL:
            if isinstance(value, str):
                if not value.startswith(('http://', 'https://')):
                    return f"https://{value}"
                return value
            return value
        
        elif format_type == FormatType.CUSTOM:
            # 自定义格式：使用Python格式化字符串
            try:
                return target_format.format(value=value)
            except:
                return value
        
        return value
    
    def validate_format(self, value: Any, format_type: FormatType) -> bool:
        """
        验证格式
        
        Args:
            value: 值
            format_type: 格式类型
            
        Returns:
            是否有效
        """
        if value is None:
            return False
        
        if format_type == FormatType.EMAIL:
            if isinstance(value, str):
                pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                return bool(re.match(pattern, value))
            return False
        
        elif format_type == FormatType.URL:
            if isinstance(value, str):
                pattern = r'^https?://[^\s/$.?#].[^\s]*$'
                return bool(re.match(pattern, value))
            return False
        
        elif format_type == FormatType.PHONE:
            if isinstance(value, str):
                digits = re.sub(r'\D', '', value)
                return len(digits) in [10, 11]
            return False
        
        return True
    
    def get_format_stats(self) -> Dict[str, Any]:
        """
        获取格式化统计
        
        Returns:
            格式化统计
        """
        total_formats = len(self.format_history)
        total_processed = sum(r.records_processed for r in self.format_history)
        total_formatted = sum(r.records_formatted for r in self.format_history)
        
        if total_formats > 0:
            avg_time = sum(r.format_time for r in self.format_history) / total_formats
        else:
            avg_time = 0.0
        
        return {
            'total_formats': total_formats,
            'total_processed': total_processed,
            'total_formatted': total_formatted,
            'format_rate': (total_formatted / total_processed * 100) if total_processed > 0 else 0.0,
            'average_format_time': avg_time
        }


def main():
    """主函数 - 示例用法"""
    formatter = DataFormatter()
    
    # 格式化数据
    data = [
        {'name': 'Alice', 'phone': '1234567890', 'email': 'ALICE@EXAMPLE.COM'}
    ]
    
    rules = [
        FormatRule('phone', FormatType.PHONE, '(XXX) XXX-XXXX'),
        FormatRule('email', FormatType.EMAIL, 'lowercase')
    ]
    
    result = formatter.format_data(data, rules)
    print(f"格式化结果: 处理={result.records_processed}, 格式化={result.records_formatted}")


if __name__ == '__main__':
    main()
