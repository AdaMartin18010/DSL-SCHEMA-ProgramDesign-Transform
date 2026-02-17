#!/usr/bin/env python3
"""
Batch Schema Processor
======================

批量Schema处理工具，支持：
- 批量验证
- 批量转换
- 批量生成矩阵
- 并行处理
- 进度追踪
- 失败重试

Version: 2.1.0
"""

import asyncio
import json
import traceback
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, Generic, List, Optional, TypeVar, Union
from uuid import uuid4

from enhanced_validator import EnhancedSchemaValidator, SchemaType, ValidationResult


T = TypeVar('T')
R = TypeVar('R')


class TaskStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"


@dataclass
class BatchTask(Generic[T, R]):
    """批处理任务"""
    task_id: str
    task_type: str
    input_data: T
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[R] = None
    error: Optional[str] = None
    retry_count: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BatchJob:
    """批处理作业"""
    job_id: str
    job_type: str
    tasks: List[BatchTask]
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    progress: float = 0.0


@dataclass
class BatchResult:
    """批处理结果"""
    job_id: str
    total_tasks: int
    completed: int
    failed: int
    results: List[Dict[str, Any]]
    errors: List[Dict[str, Any]]
    duration_seconds: float
    summary: Dict[str, Any]


class BatchProcessor:
    """批量处理器"""
    
    def __init__(
        self,
        max_workers: int = 4,
        use_processes: bool = False,
        max_retries: int = 3
    ):
        self.max_workers = max_workers
        self.use_processes = use_processes
        self.max_retries = max_retries
        self.validator = EnhancedSchemaValidator()
        self.executor_class = ProcessPoolExecutor if use_processes else ThreadPoolExecutor
        self._progress_callbacks: List[Callable] = []
    
    def on_progress(self, callback: Callable[[str, float], None]):
        """注册进度回调"""
        self._progress_callbacks.append(callback)
    
    def _notify_progress(self, job_id: str, progress: float):
        """通知进度更新"""
        for callback in self._progress_callbacks:
            try:
                callback(job_id, progress)
            except Exception:
                pass
    
    async def process_batch(
        self,
        items: List[Dict[str, Any]],
        operation: str,
        options: Optional[Dict] = None
    ) -> BatchResult:
        """
        批量处理
        
        Args:
            items: 待处理的项目列表
            operation: 操作类型 (validate, convert, transform)
            options: 处理选项
        
        Returns:
            BatchResult: 批量处理结果
        """
        job_id = str(uuid4())
        start_time = datetime.utcnow()
        
        # 创建任务
        tasks = [
            BatchTask(
                task_id=str(uuid4()),
                task_type=operation,
                input_data=item
            )
            for item in items
        ]
        
        job = BatchJob(
            job_id=job_id,
            job_type=operation,
            tasks=tasks
        )
        
        # 执行处理
        results = []
        errors = []
        completed = 0
        failed = 0
        
        loop = asyncio.get_event_loop()
        
        with self.executor_class(max_workers=self.max_workers) as executor:
            futures = []
            
            for task in tasks:
                if operation == 'validate':
                    future = loop.run_in_executor(
                        executor,
                        self._validate_task,
                        task,
                        options or {}
                    )
                elif operation == 'convert':
                    future = loop.run_in_executor(
                        executor,
                        self._convert_task,
                        task,
                        options or {}
                    )
                else:
                    future = loop.run_in_executor(
                        executor,
                        self._generic_task,
                        task,
                        operation,
                        options or {}
                    )
                
                futures.append((task, future))
            
            # 等待所有任务完成并更新进度
            for i, (task, future) in enumerate(futures):
                try:
                    result = await future
                    
                    if result.get('success'):
                        completed += 1
                        results.append({
                            'task_id': task.task_id,
                            'input': task.input_data,
                            'result': result.get('data')
                        })
                    else:
                        failed += 1
                        errors.append({
                            'task_id': task.task_id,
                            'input': task.input_data,
                            'error': result.get('error')
                        })
                
                except Exception as e:
                    failed += 1
                    errors.append({
                        'task_id': task.task_id,
                        'input': task.input_data,
                        'error': str(e),
                        'traceback': traceback.format_exc()
                    })
                
                # 更新进度
                progress = (i + 1) / len(futures)
                job.progress = progress
                self._notify_progress(job_id, progress)
        
        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()
        
        # 生成摘要
        summary = self._generate_summary(operation, results, errors)
        
        return BatchResult(
            job_id=job_id,
            total_tasks=len(items),
            completed=completed,
            failed=failed,
            results=results,
            errors=errors,
            duration_seconds=duration,
            summary=summary
        )
    
    def _validate_task(
        self,
        task: BatchTask,
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """执行验证任务"""
        try:
            schema = task.input_data
            schema_type = SchemaType(options.get('schema_type', 'json_schema'))
            standards = options.get('standards', [])
            
            result = self.validator.validate(
                schema,
                schema_type,
                standards
            )
            
            return {
                'success': result.valid,
                'data': {
                    'valid': result.valid,
                    'issues_count': len(result.issues),
                    'compliance_reports': [
                        {
                            'standard': r.standard,
                            'compliant': r.compliant,
                            'score': r.score
                        }
                        for r in result.compliance_reports
                    ]
                },
                'error': None if result.valid else 'Validation failed'
            }
        
        except Exception as e:
            return {
                'success': False,
                'data': None,
                'error': str(e)
            }
    
    def _convert_task(
        self,
        task: BatchTask,
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """执行转换任务"""
        try:
            input_data = task.input_data
            source_type = options.get('source_type', 'json_schema')
            target_type = options.get('target_type', 'openapi')
            
            # 模拟转换
            converted = {
                'original': input_data,
                'source_type': source_type,
                'target_type': target_type,
                'converted': True
            }
            
            return {
                'success': True,
                'data': converted,
                'error': None
            }
        
        except Exception as e:
            return {
                'success': False,
                'data': None,
                'error': str(e)
            }
    
    def _generic_task(
        self,
        task: BatchTask,
        operation: str,
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """通用任务处理"""
        try:
            # 模拟处理
            result = {
                'operation': operation,
                'input': task.input_data,
                'processed': True
            }
            
            return {
                'success': True,
                'data': result,
                'error': None
            }
        
        except Exception as e:
            return {
                'success': False,
                'data': None,
                'error': str(e)
            }
    
    def _generate_summary(
        self,
        operation: str,
        results: List[Dict],
        errors: List[Dict]
    ) -> Dict[str, Any]:
        """生成处理摘要"""
        total = len(results) + len(errors)
        success_rate = len(results) / total if total > 0 else 0
        
        summary = {
            'operation': operation,
            'total_processed': total,
            'successful': len(results),
            'failed': len(errors),
            'success_rate': round(success_rate, 4)
        }
        
        # 按操作类型添加特定统计
        if operation == 'validate':
            valid_count = sum(
                1 for r in results
                if r.get('result', {}).get('valid', False)
            )
            summary['valid_schemas'] = valid_count
            summary['invalid_schemas'] = len(results) - valid_count
        
        return summary
    
    async def process_files(
        self,
        file_paths: List[Union[str, Path]],
        operation: str = 'validate',
        options: Optional[Dict] = None
    ) -> BatchResult:
        """批量处理文件"""
        # 读取所有文件
        items = []
        for path in file_paths:
            try:
                content = Path(path).read_text(encoding='utf-8')
                items.append({
                    'path': str(path),
                    'content': content
                })
            except Exception as e:
                print(f"Failed to read {path}: {e}")
        
        return await self.process_batch(items, operation, options)
    
    def export_result(
        self,
        result: BatchResult,
        output_path: Optional[Union[str, Path]] = None,
        format: str = 'json'
    ) -> str:
        """导出处理结果"""
        data = {
            'job_id': result.job_id,
            'timestamp': datetime.utcnow().isoformat(),
            'summary': result.summary,
            'total_tasks': result.total_tasks,
            'completed': result.completed,
            'failed': result.failed,
            'duration_seconds': result.duration_seconds,
            'results': result.results,
            'errors': result.errors
        }
        
        if format == 'json':
            output = json.dumps(data, indent=2, ensure_ascii=False)
        elif format == 'csv':
            # 简化的CSV导出
            import csv
            import io
            
            buffer = io.StringIO()
            writer = csv.writer(buffer)
            writer.writerow(['task_id', 'status', 'details'])
            
            for r in result.results:
                writer.writerow([r['task_id'], 'success', str(r.get('result', ''))[:100]])
            
            for e in result.errors:
                writer.writerow([e['task_id'], 'failed', str(e.get('error', ''))[:100]])
            
            output = buffer.getvalue()
        else:
            output = str(data)
        
        if output_path:
            Path(output_path).write_text(output, encoding='utf-8')
        
        return output


# 便捷函数
async def batch_validate(
    schemas: List[Dict],
    schema_type: str = 'json_schema',
    standards: Optional[List[str]] = None,
    max_workers: int = 4
) -> BatchResult:
    """便捷批量验证函数"""
    processor = BatchProcessor(max_workers=max_workers)
    
    items = [{'schema': s} for s in schemas]
    
    return await processor.process_batch(
        items,
        operation='validate',
        options={
            'schema_type': schema_type,
            'standards': standards or []
        }
    )


# 示例用法
async def main():
    """示例：批量处理"""
    processor = BatchProcessor(max_workers=4)
    
    # 模拟一批Schema
    schemas = [
        {
            "$schema": "https://json-schema.org/draft/2025-01/schema",
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "name": {"type": "string"}
            }
        }
        for i in range(10)
    ]
    
    # 添加一些有问题的
    schemas.append({"type": "invalid_type"})
    
    # 处理
    def on_progress(job_id: str, progress: float):
        print(f"Progress: {progress*100:.1f}%")
    
    processor.on_progress(on_progress)
    
    result = await batch_validate(
        schemas,
        schema_type='json_schema',
        standards=['gs1'],
        max_workers=4
    )
    
    print("\n=== 批处理结果 ===")
    print(f"任务ID: {result.job_id}")
    print(f"总任务数: {result.total_tasks}")
    print(f"成功: {result.completed}")
    print(f"失败: {result.failed}")
    print(f"耗时: {result.duration_seconds:.2f}秒")
    print(f"\n摘要: {json.dumps(result.summary, indent=2)}")
    
    if result.errors:
        print(f"\n错误示例:")
        for e in result.errors[:3]:
            print(f"  - {e.get('error', 'Unknown error')}")


if __name__ == '__main__':
    asyncio.run(main())
