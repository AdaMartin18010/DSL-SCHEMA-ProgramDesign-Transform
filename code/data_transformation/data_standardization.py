"""
数据标准化模块

专注于数据标准化、格式统一、数据规范化
"""

from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import re
import logging

logger = logging.getLogger(__name__)


class StandardizationRule(Enum):
    """标准化规则"""
    CASE_NORMALIZE = "case_normalize"  # 大小写规范化
    DATE_FORMAT = "date_format"  # 日期格式
    NUMBER_FORMAT = "number_format"  # 数字格式
    PHONE_FORMAT = "phone_format"  # 电话格式
    EMAIL_FORMAT = "email_format"  # 邮箱格式
    REMOVE_WHITESPACE = "remove_whitespace"  # 去除空白
    UNIFY_SEPARATORS = "unify_separators"  # 统一分隔符


@dataclass
class StandardizationConfig:
    """标准化配置"""
    field: str
    rule: StandardizationRule
    target_format: Optional[str] = None
    config: Dict[str, Any] = None


@dataclass
class StandardizationResult:
    """标准化结果"""
    standardization_id: str
    records_processed: int
    records_modified: int
    standardization_time: float
    data: List[Dict[str, Any]]


class DataStandardization:
    """
    数据标准化器
    
    专注于数据标准化、格式统一、数据规范化
    """
    
    def __init__(self):
        self.standardization_history: List[StandardizationResult] = []
    
    def standardize(self, data: List[Dict[str, Any]], configs: List[StandardizationConfig]) -> StandardizationResult:
        """
        标准化数据
        
        Args:
            data: 数据列表
            configs: 标准化配置列表
            
        Returns:
            标准化结果
        """
        standardization_id = f"std_{datetime.utcnow().timestamp()}"
        start_time = datetime.utcnow()
        
        standardized_data = []
        records_modified = 0
        
        for record in data:
            standardized_record = record.copy()
            modified = False
            
            for config in configs:
                if config.field in standardized_record:
                    original_value = standardized_record[config.field]
                    standardized_value = self._apply_standardization(original_value, config)
                    
                    if standardized_value != original_value:
                        standardized_record[config.field] = standardized_value
                        modified = True
            
            standardized_data.append(standardized_record)
            if modified:
                records_modified += 1
        
        end_time = datetime.utcnow()
        standardization_time = (end_time - start_time).total_seconds()
        
        result = StandardizationResult(
            standardization_id=standardization_id,
            records_processed=len(data),
            records_modified=records_modified,
            standardization_time=standardization_time,
            data=standardized_data
        )
        
        self.standardization_history.append(result)
        return result
    
    def _apply_standardization(self, value: Any, config: StandardizationConfig) -> Any:
        """应用标准化规则"""
        if value is None:
            return value
        
        rule = config.rule
        target_format = config.target_format
        rule_config = config.config or {}
        
        if rule == StandardizationRule.CASE_NORMALIZE:
            if isinstance(value, str):
                case_type = rule_config.get('case', 'lower')
                if case_type == 'lower':
                    return value.lower()
                elif case_type == 'upper':
                    return value.upper()
                elif case_type == 'title':
                    return value.title()
                elif case_type == 'capitalize':
                    return value.capitalize()
            return value
        
        elif rule == StandardizationRule.DATE_FORMAT:
            if isinstance(value, str) and target_format:
                # 简化实现：只处理ISO格式
                try:
                    dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
                    return dt.strftime(target_format)
                except:
                    return value
            return value
        
        elif rule == StandardizationRule.NUMBER_FORMAT:
            if isinstance(value, (int, float)) and target_format:
                return format(value, target_format)
            return value
        
        elif rule == StandardizationRule.PHONE_FORMAT:
            if isinstance(value, str):
                # 去除所有非数字字符
                digits = re.sub(r'\D', '', value)
                if target_format:
                    # 格式化电话号码
                    if len(digits) == 10:
                        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
                    elif len(digits) == 11:
                        return f"{digits[0]} ({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
                return digits
            return value
        
        elif rule == StandardizationRule.EMAIL_FORMAT:
            if isinstance(value, str):
                # 转换为小写并去除空白
                email = value.lower().strip()
                # 简单验证
                if '@' in email:
                    return email
            return value
        
        elif rule == StandardizationRule.REMOVE_WHITESPACE:
            if isinstance(value, str):
                return re.sub(r'\s+', ' ', value).strip()
            return value
        
        elif rule == StandardizationRule.UNIFY_SEPARATORS:
            if isinstance(value, str):
                separator = rule_config.get('separator', ',')
                # 统一分隔符
                value = re.sub(r'[,;|]', separator, value)
                return value
            return value
        
        return value
    
    def get_standardization_stats(self) -> Dict[str, Any]:
        """
        获取标准化统计
        
        Returns:
            标准化统计
        """
        total_standardizations = len(self.standardization_history)
        total_processed = sum(r.records_processed for r in self.standardization_history)
        total_modified = sum(r.records_modified for r in self.standardization_history)
        
        if total_standardizations > 0:
            avg_time = sum(r.standardization_time for r in self.standardization_history) / total_standardizations
        else:
            avg_time = 0.0
        
        return {
            'total_standardizations': total_standardizations,
            'total_processed': total_processed,
            'total_modified': total_modified,
            'modification_rate': (total_modified / total_processed * 100) if total_processed > 0 else 0.0,
            'average_standardization_time': avg_time
        }


def main():
    """主函数 - 示例用法"""
    standardization = DataStandardization()
    
    # 标准化数据
    data = [
        {'name': '  ALICE  ', 'phone': '123-456-7890', 'email': 'ALICE@EXAMPLE.COM'}
    ]
    
    configs = [
        StandardizationConfig('name', StandardizationRule.CASE_NORMALIZE, config={'case': 'title'}),
        StandardizationConfig('phone', StandardizationRule.PHONE_FORMAT, target_format='(XXX) XXX-XXXX'),
        StandardizationConfig('email', StandardizationRule.EMAIL_FORMAT)
    ]
    
    result = standardization.standardize(data, configs)
    print(f"标准化结果: 处理={result.records_processed}, 修改={result.records_modified}")


if __name__ == '__main__':
    main()
