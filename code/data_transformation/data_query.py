"""
数据查询模块

专注于数据查询、过滤、排序、分页
"""

from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class SortOrder(Enum):
    """排序顺序"""
    ASC = "asc"  # 升序
    DESC = "desc"  # 降序


class FilterOperator(Enum):
    """过滤操作符"""
    EQ = "eq"  # 等于
    NE = "ne"  # 不等于
    GT = "gt"  # 大于
    GTE = "gte"  # 大于等于
    LT = "lt"  # 小于
    LTE = "lte"  # 小于等于
    IN = "in"  # 包含
    NOT_IN = "not_in"  # 不包含
    LIKE = "like"  # 模糊匹配
    BETWEEN = "between"  # 范围


@dataclass
class QueryFilter:
    """查询过滤"""
    field: str
    operator: FilterOperator
    value: Any


@dataclass
class SortField:
    """排序字段"""
    field: str
    order: SortOrder


@dataclass
class QueryResult:
    """查询结果"""
    query_id: str
    records: List[Dict[str, Any]]
    total_count: int
    page: int
    page_size: int
    query_time: float


class DataQuery:
    """
    数据查询器
    
    专注于数据查询、过滤、排序、分页
    """
    
    def __init__(self):
        self.query_history: List[QueryResult] = []
        self.data_stores: Dict[str, List[Dict[str, Any]]] = {}
    
    def register_data_store(self, store_id: str, data: List[Dict[str, Any]]):
        """
        注册数据存储
        
        Args:
            store_id: 存储ID
            data: 数据列表
        """
        self.data_stores[store_id] = data
    
    def query(self, store_id: str, filters: Optional[List[QueryFilter]] = None,
             sort_fields: Optional[List[SortField]] = None,
             page: int = 1, page_size: int = 100) -> QueryResult:
        """
        查询数据
        
        Args:
            store_id: 存储ID
            filters: 过滤条件列表
            sort_fields: 排序字段列表
            page: 页码
            page_size: 每页大小
            
        Returns:
            查询结果
        """
        if store_id not in self.data_stores:
            raise ValueError(f"数据存储不存在: {store_id}")
        
        query_id = f"query_{datetime.utcnow().timestamp()}"
        start_time = datetime.utcnow()
        
        data = self.data_stores[store_id].copy()
        
        # 应用过滤
        if filters:
            data = self._apply_filters(data, filters)
        
        # 获取总数
        total_count = len(data)
        
        # 应用排序
        if sort_fields:
            data = self._apply_sort(data, sort_fields)
        
        # 应用分页
        start_index = (page - 1) * page_size
        end_index = start_index + page_size
        paginated_data = data[start_index:end_index]
        
        end_time = datetime.utcnow()
        query_time = (end_time - start_time).total_seconds()
        
        result = QueryResult(
            query_id=query_id,
            records=paginated_data,
            total_count=total_count,
            page=page,
            page_size=page_size,
            query_time=query_time
        )
        
        self.query_history.append(result)
        return result
    
    def _apply_filters(self, data: List[Dict[str, Any]],
                      filters: List[QueryFilter]) -> List[Dict[str, Any]]:
        """应用过滤条件"""
        filtered_data = data
        
        for filter_item in filters:
            filtered_data = [
                record for record in filtered_data
                if self._match_filter(record, filter_item)
            ]
        
        return filtered_data
    
    def _match_filter(self, record: Dict[str, Any], filter_item: QueryFilter) -> bool:
        """匹配过滤条件"""
        field_value = record.get(filter_item.field)
        operator = filter_item.operator
        filter_value = filter_item.value
        
        if operator == FilterOperator.EQ:
            return field_value == filter_value
        elif operator == FilterOperator.NE:
            return field_value != filter_value
        elif operator == FilterOperator.GT:
            return field_value is not None and field_value > filter_value
        elif operator == FilterOperator.GTE:
            return field_value is not None and field_value >= filter_value
        elif operator == FilterOperator.LT:
            return field_value is not None and field_value < filter_value
        elif operator == FilterOperator.LTE:
            return field_value is not None and field_value <= filter_value
        elif operator == FilterOperator.IN:
            return field_value in filter_value if isinstance(filter_value, list) else False
        elif operator == FilterOperator.NOT_IN:
            return field_value not in filter_value if isinstance(filter_value, list) else True
        elif operator == FilterOperator.LIKE:
            if isinstance(field_value, str) and isinstance(filter_value, str):
                return filter_value.lower() in field_value.lower()
            return False
        elif operator == FilterOperator.BETWEEN:
            if isinstance(filter_value, (list, tuple)) and len(filter_value) == 2:
                return filter_value[0] <= field_value <= filter_value[1]
            return False
        else:
            return True
    
    def _apply_sort(self, data: List[Dict[str, Any]],
                   sort_fields: List[SortField]) -> List[Dict[str, Any]]:
        """应用排序"""
        def sort_key(record):
            key_values = []
            for sort_field in sort_fields:
                value = record.get(sort_field.field)
                # 处理None值
                if value is None:
                    value = '' if sort_field.order == SortOrder.ASC else 'zzz'
                key_values.append((value, sort_field.order))
            return key_values
        
        sorted_data = sorted(data, key=sort_key)
        
        # 处理降序
        for i, sort_field in enumerate(sort_fields):
            if sort_field.order == SortOrder.DESC:
                sorted_data = sorted(sorted_data, key=lambda r: r.get(sort_field.field) or '', reverse=True)
                break
        
        return sorted_data
    
    def count(self, store_id: str, filters: Optional[List[QueryFilter]] = None) -> int:
        """
        统计记录数
        
        Args:
            store_id: 存储ID
            filters: 过滤条件列表
            
        Returns:
            记录数
        """
        if store_id not in self.data_stores:
            return 0
        
        data = self.data_stores[store_id].copy()
        
        if filters:
            data = self._apply_filters(data, filters)
        
        return len(data)
    
    def get_query_stats(self) -> Dict[str, Any]:
        """
        获取查询统计
        
        Returns:
            查询统计
        """
        total_queries = len(self.query_history)
        total_records_queried = sum(q.total_count for q in self.query_history)
        
        if total_queries > 0:
            avg_time = sum(q.query_time for q in self.query_history) / total_queries
        else:
            avg_time = 0.0
        
        return {
            'total_queries': total_queries,
            'total_records_queried': total_records_queried,
            'average_query_time': avg_time
        }


def main():
    """主函数 - 示例用法"""
    query = DataQuery()
    
    # 注册数据存储
    query.register_data_store('users', [
        {'id': 1, 'name': 'Alice', 'age': 25, 'city': 'Beijing'},
        {'id': 2, 'name': 'Bob', 'age': 30, 'city': 'Shanghai'},
        {'id': 3, 'name': 'Charlie', 'age': 25, 'city': 'Beijing'}
    ])
    
    # 查询数据
    filters = [
        QueryFilter('age', FilterOperator.GTE, 25),
        QueryFilter('city', FilterOperator.EQ, 'Beijing')
    ]
    sort_fields = [SortField('age', SortOrder.ASC)]
    
    result = query.query('users', filters=filters, sort_fields=sort_fields, page=1, page_size=10)
    print(f"查询结果: 总数={result.total_count}, 返回记录数={len(result.records)}")


if __name__ == '__main__':
    main()
