"""
Tests for Batch Processor
=========================

测试覆盖：
- 批量验证
- 批量转换
- 并行处理
- 进度追踪
- 失败重试

Version: 2.1.0
"""

import pytest
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'Tools'))

from batch_processor import (
    BatchProcessor, BatchTask, BatchJob, BatchResult,
    TaskStatus, batch_validate
)


class TestBatchProcessor:
    """批量处理器测试"""
    
    @pytest.fixture
    def processor(self):
        return BatchProcessor(max_workers=2)
    
    @pytest.mark.asyncio
    async def test_process_batch_validate(self, processor):
        """测试批量验证"""
        items = [
            {"schema": {"type": "object"}, "name": "schema1"},
            {"schema": {"type": "string"}, "name": "schema2"}
        ]
        
        result = await processor.process_batch(items, 'validate')
        
        assert isinstance(result, BatchResult)
        assert result.total_tasks == 2
        assert result.completed > 0
    
    @pytest.mark.asyncio
    async def test_process_batch_with_progress(self, processor):
        """测试带进度回调的批量处理"""
        progress_updates = []
        
        def on_progress(job_id: str, progress: float):
            progress_updates.append((job_id, progress))
        
        processor.on_progress(on_progress)
        
        items = [{"data": i} for i in range(5)]
        result = await processor.process_batch(items, 'generic')
        
        assert len(progress_updates) > 0
        assert result.total_tasks == 5
    
    @pytest.mark.asyncio
    async def test_process_batch_empty(self, processor):
        """测试空批量处理"""
        result = await processor.process_batch([], 'validate')
        
        assert result.total_tasks == 0
        assert result.completed == 0
        assert result.failed == 0
    
    def test_validate_task_success(self, processor):
        """测试验证任务成功"""
        task = BatchTask(
            task_id="test-1",
            task_type="validate",
            input_data={"schema": {"type": "object"}}
        )
        
        result = processor._validate_task(task, {})
        
        assert result['success'] is True
        assert 'data' in result
    
    def test_validate_task_failure(self, processor):
        """测试验证任务失败"""
        task = BatchTask(
            task_id="test-1",
            task_type="validate",
            input_data=None  # 无效输入
        )
        
        result = processor._validate_task(task, {})
        
        assert result['success'] is False
        assert 'error' in result
    
    def test_export_result_json(self, processor, tmp_path):
        """测试JSON格式导出"""
        result = BatchResult(
            job_id="test-job",
            total_tasks=10,
            completed=8,
            failed=2,
            results=[],
            errors=[],
            duration_seconds=5.0,
            summary={"test": True}
        )
        
        output_file = tmp_path / "result.json"
        exported = processor.export_result(result, str(output_file), 'json')
        
        assert output_file.exists()
        assert "test-job" in exported
        assert "summary" in exported
    
    def test_export_result_csv(self, processor, tmp_path):
        """测试CSV格式导出"""
        result = BatchResult(
            job_id="test-job",
            total_tasks=2,
            completed=1,
            failed=1,
            results=[{"task_id": "1"}],
            errors=[{"task_id": "2"}],
            duration_seconds=1.0,
            summary={}
        )
        
        output_file = tmp_path / "result.csv"
        exported = processor.export_result(result, str(output_file), 'csv')
        
        assert output_file.exists()
        assert "task_id" in exported


class TestBatchValidate:
    """批量验证便捷函数测试"""
    
    @pytest.mark.asyncio
    async def test_batch_validate_basic(self):
        """测试基本批量验证"""
        schemas = [
            {"type": "object"},
            {"type": "string"}
        ]
        
        result = await batch_validate(schemas)
        
        assert result.total_tasks == 2
        assert result.completed >= 0
        assert "validate" in result.summary.get("operation", "")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
