"""
数据加载模块

专注于数据加载、批量加载、增量加载
"""

from typing import Dict, List, Any, Optional, Callable, Iterator
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class LoadMode(Enum):
    """加载模式"""
    INSERT = "insert"  # 插入
    UPSERT = "upsert"  # 更新插入
    REPLACE = "replace"  # 替换
    APPEND = "append"  # 追加
    MERGE = "merge"  # 合并


class LoadStrategy(Enum):
    """加载策略"""
    BATCH = "batch"  # 批处理
    STREAM = "stream"  # 流处理
    INCREMENTAL = "incremental"  # 增量


@dataclass
class LoadResult:
    """加载结果"""
    load_id: str
    records_loaded: int
    records_failed: int
    load_time: float
    success: bool
    errors: List[Dict[str, Any]] = None


class DataLoader:
    """
    数据加载器
    
    专注于数据加载、批量加载、增量加载
    """
    
    def __init__(self, batch_size: int = 1000):
        self.batch_size = batch_size
        self.load_history: List[LoadResult] = []
        self.data_stores: Dict[str, List[Dict[str, Any]]] = {}
    
    def register_data_store(self, store_id: str):
        """
        注册数据存储
        
        Args:
            store_id: 存储ID
        """
        if store_id not in self.data_stores:
            self.data_stores[store_id] = []
    
    def load_data(self, store_id: str, data: List[Dict[str, Any]],
                 load_mode: LoadMode = LoadMode.INSERT,
                 load_strategy: LoadStrategy = LoadStrategy.BATCH,
                 key_fields: Optional[List[str]] = None) -> LoadResult:
        """
        加载数据
        
        Args:
            store_id: 存储ID
            data: 数据列表
            load_mode: 加载模式
            load_strategy: 加载策略
            key_fields: 关键字段列表（用于更新插入）
            
        Returns:
            加载结果
        """
        self.register_data_store(store_id)
        
        load_id = f"load_{datetime.utcnow().timestamp()}"
        start_time = datetime.utcnow()
        
        records_loaded = 0
        records_failed = 0
        errors = []
        
        try:
            if load_strategy == LoadStrategy.BATCH:
                records_loaded, records_failed, errors = self._batch_load(
                    store_id, data, load_mode, key_fields
                )
            elif load_strategy == LoadStrategy.STREAM:
                records_loaded, records_failed, errors = self._stream_load(
                    store_id, data, load_mode, key_fields
                )
            elif load_strategy == LoadStrategy.INCREMENTAL:
                records_loaded, records_failed, errors = self._incremental_load(
                    store_id, data, load_mode, key_fields
                )
            else:
                records_loaded, records_failed, errors = self._batch_load(
                    store_id, data, load_mode, key_fields
                )
        
        except Exception as e:
            logger.error(f"加载失败: {e}")
            records_failed = len(data)
            errors.append({'error': str(e)})
        
        end_time = datetime.utcnow()
        load_time = (end_time - start_time).total_seconds()
        
        result = LoadResult(
            load_id=load_id,
            records_loaded=records_loaded,
            records_failed=records_failed,
            load_time=load_time,
            success=records_failed == 0,
            errors=errors
        )
        
        self.load_history.append(result)
        return result
    
    def _batch_load(self, store_id: str, data: List[Dict[str, Any]],
                   load_mode: LoadMode, key_fields: Optional[List[str]]) -> tuple[int, int, List[Dict[str, Any]]]:
        """批处理加载"""
        records_loaded = 0
        records_failed = 0
        errors = []
        
        store = self.data_stores[store_id]
        
        for i, record in enumerate(data):
            try:
                if load_mode == LoadMode.INSERT:
                    store.append(record)
                    records_loaded += 1
                
                elif load_mode == LoadMode.UPSERT:
                    if key_fields:
                        # 查找现有记录
                        existing_index = self._find_record(store, record, key_fields)
                        if existing_index is not None:
                            store[existing_index] = record  # 更新
                        else:
                            store.append(record)  # 插入
                        records_loaded += 1
                    else:
                        store.append(record)
                        records_loaded += 1
                
                elif load_mode == LoadMode.REPLACE:
                    store.clear()
                    store.extend(data)
                    records_loaded = len(data)
                    break  # 替换后退出循环
                
                elif load_mode == LoadMode.APPEND:
                    store.append(record)
                    records_loaded += 1
                
                elif load_mode == LoadMode.MERGE:
                    if key_fields:
                        existing_index = self._find_record(store, record, key_fields)
                        if existing_index is not None:
                            # 合并记录
                            store[existing_index] = {**store[existing_index], **record}
                        else:
                            store.append(record)
                        records_loaded += 1
                    else:
                        store.append(record)
                        records_loaded += 1
            
            except Exception as e:
                records_failed += 1
                errors.append({
                    'index': i,
                    'record': record,
                    'error': str(e)
                })
        
        return records_loaded, records_failed, errors
    
    def _stream_load(self, store_id: str, data: List[Dict[str, Any]],
                    load_mode: LoadMode, key_fields: Optional[List[str]]) -> tuple[int, int, List[Dict[str, Any]]]:
        """流处理加载"""
        # 简化实现：使用批处理
        return self._batch_load(store_id, data, load_mode, key_fields)
    
    def _incremental_load(self, store_id: str, data: List[Dict[str, Any]],
                         load_mode: LoadMode, key_fields: Optional[List[str]]) -> tuple[int, int, List[Dict[str, Any]]]:
        """增量加载"""
        # 增量加载通常使用更新插入模式
        if load_mode == LoadMode.INSERT:
            load_mode = LoadMode.UPSERT
        
        return self._batch_load(store_id, data, load_mode, key_fields)
    
    def _find_record(self, store: List[Dict[str, Any]], record: Dict[str, Any],
                    key_fields: List[str]) -> Optional[int]:
        """查找记录"""
        record_key = tuple(record.get(f) for f in key_fields)
        
        for i, existing_record in enumerate(store):
            existing_key = tuple(existing_record.get(f) for f in key_fields)
            if existing_key == record_key:
                return i
        
        return None
    
    def get_load_stats(self) -> Dict[str, Any]:
        """
        获取加载统计
        
        Returns:
            加载统计
        """
        total_loads = len(self.load_history)
        successful_loads = sum(1 for l in self.load_history if l.success)
        total_records_loaded = sum(l.records_loaded for l in self.load_history)
        total_records_failed = sum(l.records_failed for l in self.load_history)
        
        if total_loads > 0:
            avg_time = sum(l.load_time for l in self.load_history) / total_loads
        else:
            avg_time = 0.0
        
        return {
            'total_loads': total_loads,
            'successful_loads': successful_loads,
            'failed_loads': total_loads - successful_loads,
            'total_records_loaded': total_records_loaded,
            'total_records_failed': total_records_failed,
            'success_rate': (successful_loads / total_loads * 100) if total_loads > 0 else 0.0,
            'average_load_time': avg_time
        }


def main():
    """主函数 - 示例用法"""
    loader = DataLoader()
    
    # 加载数据
    data = [
        {'id': 1, 'name': 'Alice', 'age': 25},
        {'id': 2, 'name': 'Bob', 'age': 30}
    ]
    
    result = loader.load_data('store1', data, LoadMode.INSERT)
    print(f"加载结果: 成功={result.success}, 加载记录数={result.records_loaded}")


if __name__ == '__main__':
    main()
