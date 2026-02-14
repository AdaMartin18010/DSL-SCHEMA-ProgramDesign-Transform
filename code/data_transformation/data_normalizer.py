"""
数据规范化器

专注于数据规范化处理
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class NormalizationType(Enum):
    """规范化类型"""
    MIN_MAX = "min_max"  # 最小-最大规范化
    Z_SCORE = "z_score"  # Z分数规范化
    DECIMAL_SCALING = "decimal_scaling"  # 小数定标规范化
    UNIT_VECTOR = "unit_vector"  # 单位向量规范化


@dataclass
class NormalizationConfig:
    """规范化配置"""
    config_id: str
    field: str
    normalization_type: NormalizationType
    parameters: Dict[str, Any]
    created_at: datetime


class DataNormalizer:
    """
    数据规范化器
    
    专注于数据规范化处理
    """
    
    def __init__(self):
        self.configs: Dict[str, NormalizationConfig] = {}
        self.statistics: Dict[str, Dict[str, float]] = {}
    
    def compute_statistics(self, field: str, data: List[float]) -> Dict[str, float]:
        """
        计算统计量
        
        Args:
            field: 字段名
            data: 数据列表
            
        Returns:
            统计量字典
        """
        if not data:
            return {}
        
        stats = {
            'min': min(data),
            'max': max(data),
            'mean': sum(data) / len(data),
            'std': self._calculate_std(data)
        }
        
        self.statistics[field] = stats
        return stats
    
    def _calculate_std(self, data: List[float]) -> float:
        """计算标准差"""
        if not data:
            return 0.0
        
        mean = sum(data) / len(data)
        variance = sum((x - mean) ** 2 for x in data) / len(data)
        return variance ** 0.5
    
    def normalize(self, field: str, value: float, normalization_type: NormalizationType) -> float:
        """
        规范化单个值
        
        Args:
            field: 字段名
            value: 值
            normalization_type: 规范化类型
            
        Returns:
            规范化后的值
        """
        if field not in self.statistics:
            return value
        
        stats = self.statistics[field]
        
        if normalization_type == NormalizationType.MIN_MAX:
            return self._min_max_normalize(value, stats['min'], stats['max'])
        elif normalization_type == NormalizationType.Z_SCORE:
            return self._z_score_normalize(value, stats['mean'], stats['std'])
        elif normalization_type == NormalizationType.DECIMAL_SCALING:
            return self._decimal_scaling_normalize(value, stats['max'])
        else:
            return value
    
    def _min_max_normalize(self, value: float, min_val: float, max_val: float) -> float:
        """最小-最大规范化"""
        if max_val == min_val:
            return 0.0
        return (value - min_val) / (max_val - min_val)
    
    def _z_score_normalize(self, value: float, mean: float, std: float) -> float:
        """Z分数规范化"""
        if std == 0:
            return 0.0
        return (value - mean) / std
    
    def _decimal_scaling_normalize(self, value: float, max_val: float) -> float:
        """小数定标规范化"""
        if max_val == 0:
            return 0.0
        
        # 计算需要的位数
        j = len(str(int(abs(max_val))))
        return value / (10 ** j)
    
    def normalize_field(self, field: str, data: List[Dict[str, Any]],
                       normalization_type: NormalizationType) -> List[Dict[str, Any]]:
        """
        规范化字段
        
        Args:
            field: 字段名
            data: 数据列表
            normalization_type: 规范化类型
            
        Returns:
            规范化后的数据列表
        """
        # 提取字段值
        values = [record.get(field) for record in data if field in record and isinstance(record[field], (int, float))]
        
        if not values:
            return data
        
        # 计算统计量
        stats = self.compute_statistics(field, values)
        
        # 规范化
        normalized_data = []
        value_index = 0
        
        for record in data:
            new_record = record.copy()
            
            if field in record and isinstance(record[field], (int, float)):
                new_record[field] = self.normalize(field, record[field], normalization_type)
                value_index += 1
            
            normalized_data.append(new_record)
        
        return normalized_data
    
    def denormalize(self, field: str, normalized_value: float,
                   normalization_type: NormalizationType) -> float:
        """
        反规范化
        
        Args:
            field: 字段名
            normalized_value: 规范化后的值
            normalization_type: 规范化类型
            
        Returns:
            原始值
        """
        if field not in self.statistics:
            return normalized_value
        
        stats = self.statistics[field]
        
        if normalization_type == NormalizationType.MIN_MAX:
            return self._min_max_denormalize(normalized_value, stats['min'], stats['max'])
        elif normalization_type == NormalizationType.Z_SCORE:
            return self._z_score_denormalize(normalized_value, stats['mean'], stats['std'])
        else:
            return normalized_value
    
    def _min_max_denormalize(self, normalized_value: float, min_val: float, max_val: float) -> float:
        """最小-最大反规范化"""
        return normalized_value * (max_val - min_val) + min_val
    
    def _z_score_denormalize(self, normalized_value: float, mean: float, std: float) -> float:
        """Z分数反规范化"""
        return normalized_value * std + mean


def main():
    """主函数 - 示例用法"""
    normalizer = DataNormalizer()
    
    # 示例数据
    data = [
        {'id': 1, 'score': 85.5},
        {'id': 2, 'score': 92.0},
        {'id': 3, 'score': 78.5},
        {'id': 4, 'score': 95.0},
    ]
    
    # 规范化
    normalized_data = normalizer.normalize_field(
        'score',
        data,
        NormalizationType.MIN_MAX
    )
    
    print("规范化后的数据:")
    for record in normalized_data:
        print(f"ID: {record['id']}, Score: {record['score']:.4f}")


if __name__ == '__main__':
    main()
