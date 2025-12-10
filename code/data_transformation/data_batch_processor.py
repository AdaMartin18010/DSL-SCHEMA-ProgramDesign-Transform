"""
数据批处理模块

专注于数据批处理、批量转换、批量操作
"""

from typing import Dict, List, Any, Optional, Callable, Iterator
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)


class BatchOperation(Enum):
    """批处理操作"""
    TRANSFORM = "transform"  # 转换
    VALIDATE = "validate"  # 验证
    FILTER = "filter"  # 过滤
    AGGREGATE = "aggregate"  # 聚合
    ENRICH = "enrich"  # 丰富化


@dataclass
class BatchResult:
    """批处理结果"""
    batch_id: str
    total_records: int
    processed_records: int
    failed_records: int
    success_rate: float
    processing_time: float
    results: List[Any] = None
    errors: List[Dict[str, Any]] = None


class DataBatchProcessor:
    """
    数据批处理器
    
    专注于数据批处理、批量转换、批量操作
    """
    
    def __init__(self, batch_size: int = 1000, max_workers: int = 4):
        self.batch_size = batch_size
        self.max_workers = max_workers
        self.batch_history: List[BatchResult] = []
    
    def process_batch(self, data: List[Any], operation: Callable[[Any], Any],
                     operation_type: BatchOperation = BatchOperation.TRANSFORM,
                     parallel: bool = False) -> BatchResult:
        """
        处理批次数据
        
        Args:
            data: 数据列表
            operation: 处理函数
            operation_type: 操作类型
            parallel: 是否并行处理
            
        Returns:
            批处理结果
        """
        batch_id = f"batch_{datetime.utcnow().timestamp()}"
        start_time = datetime.utcnow()
        
        total_records = len(data)
        processed_records = 0
        failed_records = 0
        results = []
        errors = []
        
        try:
            if parallel and total_records > self.batch_size:
                # 并行处理
                results, errors = self._process_parallel(data, operation)
            else:
                # 串行处理
                results, errors = self._process_sequential(data, operation)
            
            processed_records = len(results)
            failed_records = len(errors)
            
        except Exception as e:
            logger.error(f"批处理失败: {e}")
            failed_records = total_records
        
        end_time = datetime.utcnow()
        processing_time = (end_time - start_time).total_seconds()
        success_rate = (processed_records / total_records * 100) if total_records > 0 else 0.0
        
        result = BatchResult(
            batch_id=batch_id,
            total_records=total_records,
            processed_records=processed_records,
            failed_records=failed_records,
            success_rate=success_rate,
            processing_time=processing_time,
            results=results,
            errors=errors
        )
        
        self.batch_history.append(result)
        return result
    
    def _process_sequential(self, data: List[Any],
                          operation: Callable[[Any], Any]) -> tuple[List[Any], List[Dict[str, Any]]]:
        """串行处理"""
        results = []
        errors = []
        
        for i, item in enumerate(data):
            try:
                result = operation(item)
                results.append(result)
            except Exception as e:
                errors.append({
                    'index': i,
                    'item': item,
                    'error': str(e)
                })
        
        return results, errors
    
    def _process_parallel(self, data: List[Any],
                         operation: Callable[[Any], Any]) -> tuple[List[Any], List[Dict[str, Any]]]:
        """并行处理"""
        results = []
        errors = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_index = {
                executor.submit(operation, item): i
                for i, item in enumerate(data)
            }
            
            for future in as_completed(future_to_index):
                index = future_to_index[future]
                try:
                    result = future.result()
                    results.append((index, result))
                except Exception as e:
                    errors.append({
                        'index': index,
                        'error': str(e)
                    })
        
        # 按索引排序结果
        results.sort(key=lambda x: x[0])
        results = [r[1] for r in results]
        
        return results, errors
    
    def batch_transform(self, data: List[Any], transform_func: Callable[[Any], Any],
                       parallel: bool = False) -> BatchResult:
        """
        批量转换
        
        Args:
            data: 数据列表
            transform_func: 转换函数
            parallel: 是否并行处理
            
        Returns:
            批处理结果
        """
        return self.process_batch(data, transform_func, BatchOperation.TRANSFORM, parallel)
    
    def batch_validate(self, data: List[Any], validate_func: Callable[[Any], bool],
                      parallel: bool = False) -> BatchResult:
        """
        批量验证
        
        Args:
            data: 数据列表
            validate_func: 验证函数
            parallel: 是否并行处理
            
        Returns:
            批处理结果
        """
        def validator(item):
            is_valid = validate_func(item)
            return {'item': item, 'valid': is_valid}
        
        return self.process_batch(data, validator, BatchOperation.VALIDATE, parallel)
    
    def batch_filter(self, data: List[Any], filter_func: Callable[[Any], bool],
                    parallel: bool = False) -> List[Any]:
        """
        批量过滤
        
        Args:
            data: 数据列表
            filter_func: 过滤函数
            parallel: 是否并行处理
            
        Returns:
            过滤后的数据列表
        """
        def filter_processor(item):
            return item if filter_func(item) else None
        
        result = self.process_batch(data, filter_processor, BatchOperation.FILTER, parallel)
        return [r for r in result.results if r is not None]
    
    def batch_aggregate(self, data: List[Any], aggregate_func: Callable[[List[Any]], Any],
                       batch_size: Optional[int] = None) -> Any:
        """
        批量聚合
        
        Args:
            data: 数据列表
            aggregate_func: 聚合函数
            batch_size: 批次大小（可选）
            
        Returns:
            聚合结果
        """
        batch_size = batch_size or self.batch_size
        
        # 分批处理
        batches = [data[i:i + batch_size] for i in range(0, len(data), batch_size)]
        
        batch_results = []
        for batch in batches:
            try:
                result = aggregate_func(batch)
                batch_results.append(result)
            except Exception as e:
                logger.error(f"批次聚合失败: {e}")
        
        # 最终聚合
        if batch_results:
            return aggregate_func(batch_results)
        
        return None
    
    def get_batch_stats(self) -> Dict[str, Any]:
        """
        获取批处理统计
        
        Returns:
            批处理统计
        """
        if not self.batch_history:
            return {
                'total_batches': 0,
                'average_success_rate': 0.0
            }
        
        total_batches = len(self.batch_history)
        avg_success_rate = sum(b.success_rate for b in self.batch_history) / total_batches
        avg_processing_time = sum(b.processing_time for b in self.batch_history) / total_batches
        
        return {
            'total_batches': total_batches,
            'average_success_rate': avg_success_rate,
            'average_processing_time': avg_processing_time
        }


def main():
    """主函数 - 示例用法"""
    processor = DataBatchProcessor(batch_size=100, max_workers=4)
    
    # 批量转换
    data = [{'id': i, 'value': i * 2} for i in range(1000)]
    
    def transform(item):
        item['doubled'] = item['value'] * 2
        return item
    
    result = processor.batch_transform(data, transform, parallel=True)
    print(f"批处理结果: 成功率={result.success_rate:.2f}%, 处理时间={result.processing_time:.3f}秒")


if __name__ == '__main__':
    main()
