"""
数据画像器

专注于数据画像和统计分析
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from collections import Counter


@dataclass
class ColumnProfile:
    """列画像"""
    column_name: str
    data_type: str
    total_count: int
    null_count: int
    null_percentage: float
    unique_count: int
    unique_percentage: float
    min_value: Optional[Any] = None
    max_value: Optional[Any] = None
    mean_value: Optional[float] = None
    median_value: Optional[float] = None
    std_dev: Optional[float] = None
    value_distribution: Dict[str, int] = None


@dataclass
class TableProfile:
    """表画像"""
    table_name: str
    total_rows: int
    total_columns: int
    column_profiles: List[ColumnProfile]
    created_at: datetime


class DataProfiler:
    """
    数据画像器
    
    专注于数据画像和统计分析
    """
    
    def __init__(self):
        self.profiles: Dict[str, TableProfile] = {}
    
    def profile_table(self, table_name: str, data: List[Dict[str, Any]]) -> TableProfile:
        """
        画像表数据
        
        Args:
            table_name: 表名
            data: 数据列表
            
        Returns:
            表画像
        """
        if not data:
            return TableProfile(
                table_name=table_name,
                total_rows=0,
                total_columns=0,
                column_profiles=[],
                created_at=datetime.utcnow()
            )
        
        # 获取所有列名
        columns = set()
        for record in data:
            columns.update(record.keys())
        
        # 为每列生成画像
        column_profiles = []
        for column in columns:
            column_profile = self._profile_column(column, data)
            column_profiles.append(column_profile)
        
        profile = TableProfile(
            table_name=table_name,
            total_rows=len(data),
            total_columns=len(columns),
            column_profiles=column_profiles,
            created_at=datetime.utcnow()
        )
        
        self.profiles[table_name] = profile
        return profile
    
    def _profile_column(self, column_name: str, data: List[Dict[str, Any]]) -> ColumnProfile:
        """画像单个列"""
        values = [record.get(column_name) for record in data]
        
        # 基本统计
        total_count = len(values)
        null_count = sum(1 for v in values if v is None)
        null_percentage = (null_count / total_count * 100) if total_count > 0 else 0.0
        
        # 非空值
        non_null_values = [v for v in values if v is not None]
        unique_count = len(set(non_null_values))
        unique_percentage = (unique_count / len(non_null_values) * 100) if non_null_values else 0.0
        
        # 推断数据类型
        data_type = self._infer_data_type(non_null_values)
        
        # 数值统计
        min_value = None
        max_value = None
        mean_value = None
        median_value = None
        std_dev = None
        
        if data_type in ['integer', 'float']:
            numeric_values = [v for v in non_null_values if isinstance(v, (int, float))]
            if numeric_values:
                min_value = min(numeric_values)
                max_value = max(numeric_values)
                mean_value = sum(numeric_values) / len(numeric_values)
                sorted_values = sorted(numeric_values)
                n = len(sorted_values)
                median_value = (sorted_values[n//2] + sorted_values[(n-1)//2]) / 2 if n > 0 else None
                
                # 标准差
                if len(numeric_values) > 1:
                    variance = sum((x - mean_value) ** 2 for x in numeric_values) / len(numeric_values)
                    std_dev = variance ** 0.5
        
        # 值分布（前10个最常见的值）
        value_distribution = {}
        if non_null_values:
            counter = Counter(non_null_values)
            value_distribution = dict(counter.most_common(10))
        
        return ColumnProfile(
            column_name=column_name,
            data_type=data_type,
            total_count=total_count,
            null_count=null_count,
            null_percentage=null_percentage,
            unique_count=unique_count,
            unique_percentage=unique_percentage,
            min_value=min_value,
            max_value=max_value,
            mean_value=mean_value,
            median_value=median_value,
            std_dev=std_dev,
            value_distribution=value_distribution
        )
    
    def _infer_data_type(self, values: List[Any]) -> str:
        """推断数据类型"""
        if not values:
            return 'unknown'
        
        # 检查是否为整数
        if all(isinstance(v, int) for v in values):
            return 'integer'
        
        # 检查是否为浮点数
        if all(isinstance(v, (int, float)) for v in values):
            return 'float'
        
        # 检查是否为布尔值
        if all(isinstance(v, bool) for v in values):
            return 'boolean'
        
        # 检查是否为日期
        if all(isinstance(v, (str, datetime)) for v in values):
            # 简化实现：假设字符串可能是日期
            return 'string'
        
        # 默认为字符串
        return 'string'
    
    def get_profile_summary(self, table_name: str) -> Dict[str, Any]:
        """
        获取画像摘要
        
        Args:
            table_name: 表名
            
        Returns:
            画像摘要
        """
        if table_name not in self.profiles:
            return {}
        
        profile = self.profiles[table_name]
        
        summary = {
            'table_name': table_name,
            'total_rows': profile.total_rows,
            'total_columns': profile.total_columns,
            'columns': []
        }
        
        for col_profile in profile.column_profiles:
            summary['columns'].append({
                'name': col_profile.column_name,
                'data_type': col_profile.data_type,
                'null_percentage': col_profile.null_percentage,
                'unique_percentage': col_profile.unique_percentage
            })
        
        return summary
    
    def compare_profiles(self, table1: str, table2: str) -> Dict[str, Any]:
        """
        比较两个表的画像
        
        Args:
            table1: 表1名称
            table2: 表2名称
            
        Returns:
            比较结果
        """
        if table1 not in self.profiles or table2 not in self.profiles:
            return {'error': '表画像不存在'}
        
        profile1 = self.profiles[table1]
        profile2 = self.profiles[table2]
        
        comparison = {
            'table1': table1,
            'table2': table2,
            'row_count_diff': profile1.total_rows - profile2.total_rows,
            'column_count_diff': profile1.total_columns - profile2.total_columns,
            'common_columns': [],
            'unique_to_table1': [],
            'unique_to_table2': []
        }
        
        # 比较列
        cols1 = {c.column_name for c in profile1.column_profiles}
        cols2 = {c.column_name for c in profile2.column_profiles}
        
        comparison['common_columns'] = list(cols1 & cols2)
        comparison['unique_to_table1'] = list(cols1 - cols2)
        comparison['unique_to_table2'] = list(cols2 - cols1)
        
        return comparison


def main():
    """主函数 - 示例用法"""
    profiler = DataProfiler()
    
    # 画像数据
    sample_data = [
        {'id': 1, 'name': 'Alice', 'age': 30, 'score': 85.5},
        {'id': 2, 'name': 'Bob', 'age': 25, 'score': 92.0},
        {'id': 3, 'name': 'Charlie', 'age': None, 'score': 78.5},
    ]
    
    profile = profiler.profile_table('users', sample_data)
    print(f"画像表: {profile.table_name}")
    print(f"总行数: {profile.total_rows}")
    print(f"总列数: {profile.total_columns}")
    
    # 获取摘要
    summary = profiler.get_profile_summary('users')
    print(f"摘要: {summary}")


if __name__ == '__main__':
    main()
