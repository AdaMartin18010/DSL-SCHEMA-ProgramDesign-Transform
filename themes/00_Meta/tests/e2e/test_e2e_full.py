"""
End-to-End Integration Tests
============================

完整端到端测试套件，验证整个系统的集成功能。

测试覆盖：
- API端到端流程
- 数据库持久化
- 缓存一致性
- ML推荐服务
- 异步任务处理

运行方式：
    pytest tests/e2e/test_e2e_full.py -v
"""

import json
import time
import uuid
from datetime import datetime
from typing import Dict, Generator

import pytest
import requests

# 测试配置
BASE_URL = "http://localhost:8000"
API_PREFIX = "/api/v1"
TIMEOUT = 30


@pytest.fixture(scope="module")
def base_url() -> str:
    """基础URL"""
    return BASE_URL


@pytest.fixture
def unique_id() -> str:
    """生成唯一ID"""
    return str(uuid.uuid4())[:8]


@pytest.fixture
def sample_schema() -> Dict:
    """示例Schema"""
    return {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "$id": f"https://example.com/test-schema-{uuid.uuid4().hex[:8]}",
        "title": "Test Product",
        "type": "object",
        "properties": {
            "id": {"type": "string"},
            "name": {"type": "string", "minLength": 1},
            "price": {"type": "number", "minimum": 0},
            "category": {
                "type": "string",
                "enum": ["electronics", "clothing", "food"]
            }
        },
        "required": ["id", "name", "price"]
    }


class TestHealthAndReadiness:
    """健康检查和就绪性测试"""
    
    def test_health_endpoint(self, base_url: str):
        """测试健康检查端点"""
        response = requests.get(f"{base_url}/health", timeout=TIMEOUT)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
    
    def test_ready_endpoint(self, base_url: str):
        """测试就绪检查端点"""
        response = requests.get(f"{base_url}/ready", timeout=TIMEOUT)
        assert response.status_code == 200
        data = response.json()
        assert data["ready"] is True


class TestSchemaValidationE2E:
    """Schema验证端到端测试"""
    
    def test_full_validation_workflow(self, base_url: str, sample_schema: Dict):
        """完整验证工作流"""
        # 1. 提交Schema进行验证
        response = requests.post(
            f"{base_url}{API_PREFIX}/validate",
            json={
                "schema": sample_schema,
                "schema_type": "json_schema",
                "options": {
                    "check_references": True,
                    "check_circular": True,
                    "strict_mode": True
                }
            },
            timeout=TIMEOUT
        )
        assert response.status_code == 200
        
        result = response.json()
        assert result["valid"] is True
        assert "validation_id" in result
        
        validation_id = result["validation_id"]
        
        # 2. 查询验证结果
        time.sleep(1)  # 等待处理完成
        
        response = requests.get(
            f"{base_url}{API_PREFIX}/validate/{validation_id}",
            timeout=TIMEOUT
        )
        assert response.status_code == 200
        
        status_result = response.json()
        assert status_result["status"] in ["completed", "processing"]
    
    def test_validation_with_standard_compliance(self, base_url: str):
        """测试带标准合规性检查的验证"""
        schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "gtin": {
                    "type": "string",
                    "pattern": "^[0-9]{8,14}$"
                },
                "name": {"type": "string"},
                "price": {"type": "number"}
            },
            "required": ["gtin", "name"]
        }
        
        response = requests.post(
            f"{base_url}{API_PREFIX}/validate",
            json={
                "schema": schema,
                "schema_type": "json_schema",
                "standards": ["gs1", "iso20022"]
            },
            timeout=TIMEOUT
        )
        
        assert response.status_code == 200
        result = response.json()
        
        assert "compliance" in result
        assert "gs1" in result["compliance"]
        assert "iso20022" in result["compliance"]
    
    def test_validation_error_handling(self, base_url: str):
        """测试验证错误处理"""
        invalid_schema = {
            "type": "invalid_type",
            "properties": "not_an_object"
        }
        
        response = requests.post(
            f"{base_url}{API_PREFIX}/validate",
            json={
                "schema": invalid_schema,
                "schema_type": "json_schema"
            },
            timeout=TIMEOUT
        )
        
        assert response.status_code == 400
        result = response.json()
        assert "error" in result
        assert "details" in result


class TestMatrixGenerationE2E:
    """矩阵生成端到端测试"""
    
    def test_full_matrix_generation(self, base_url: str):
        """完整矩阵生成流程"""
        # 1. 提交矩阵生成请求
        themes = ["01_Industrial_Automation", "04_Financial_Services"]
        
        response = requests.post(
            f"{base_url}{API_PREFIX}/matrix/generate",
            json={
                "themes": themes,
                "dimensions": ["theory", "application", "standards", "tools", "industry"],
                "include_similarity": True
            },
            timeout=TIMEOUT
        )
        
        assert response.status_code == 202
        result = response.json()
        assert "task_id" in result
        
        task_id = result["task_id"]
        
        # 2. 轮询任务状态
        max_retries = 30
        for i in range(max_retries):
            response = requests.get(
                f"{base_url}{API_PREFIX}/tasks/{task_id}",
                timeout=TIMEOUT
            )
            
            if response.status_code == 200:
                status = response.json()
                if status["status"] == "completed":
                    break
                elif status["status"] == "failed":
                    pytest.fail(f"Task failed: {status.get('error')}")
            
            time.sleep(1)
        else:
            pytest.fail("Task timeout")
        
        # 3. 获取结果
        response = requests.get(
            f"{base_url}{API_PREFIX}/matrix/result/{task_id}",
            timeout=TIMEOUT
        )
        
        assert response.status_code == 200
        matrix = response.json()
        assert "themes" in matrix
        assert "matrix" in matrix
        assert len(matrix["themes"]) == len(themes)


class TestSearchE2E:
    """搜索功能端到端测试"""
    
    def test_full_text_search(self, base_url: str):
        """全文搜索功能"""
        response = requests.post(
            f"{base_url}{API_PREFIX}/search",
            json={
                "query": "data model",
                "filters": {
                    "type": ["documentation", "schema"],
                    "date_range": {
                        "from": "2024-01-01",
                        "to": "2024-12-31"
                    }
                },
                "pagination": {
                    "page": 1,
                    "per_page": 10
                }
            },
            timeout=TIMEOUT
        )
        
        assert response.status_code == 200
        result = response.json()
        assert "results" in result
        assert "total" in result
        assert "page" in result
    
    def test_search_suggestions(self, base_url: str):
        """搜索建议功能"""
        response = requests.get(
            f"{base_url}{API_PREFIX}/search/suggestions",
            params={"q": "sche"},
            timeout=TIMEOUT
        )
        
        assert response.status_code == 200
        suggestions = response.json()
        assert isinstance(suggestions, list)


class TestMLRecommendationE2E:
    """ML推荐服务端到端测试"""
    
    @pytest.mark.skip(reason="需要ML服务运行")
    def test_transformation_recommendation(self, base_url: str):
        """转换策略推荐"""
        schema_metadata = {
            "complexity_score": 0.75,
            "property_count": 50,
            "reference_count": 15,
            "industry": "financial",
            "target_standard": "iso20022"
        }
        
        response = requests.post(
            f"{base_url}{API_PREFIX}/ml/recommend",
            json={
                "task": "transformation_strategy",
                "input": schema_metadata
            },
            timeout=TIMEOUT
        )
        
        assert response.status_code == 200
        result = response.json()
        assert "recommendation" in result
        assert "confidence" in result
        assert "alternatives" in result
    
    @pytest.mark.skip(reason="需要ML服务运行")
    def test_schema_similarity_search(self, base_url: str, sample_schema: Dict):
        """相似Schema搜索"""
        response = requests.post(
            f"{base_url}{API_PREFIX}/ml/similar",
            json={
                "schema": sample_schema,
                "top_k": 5
            },
            timeout=TIMEOUT
        )
        
        assert response.status_code == 200
        result = response.json()
        assert "similar_schemas" in result
        assert len(result["similar_schemas"]) <= 5


class TestAsyncTasksE2E:
    """异步任务端到端测试"""
    
    def test_async_document_processing(self, base_url: str):
        """异步文档处理"""
        # 提交批量处理任务
        documents = [
            {"title": "Doc 1", "content": "Content 1"},
            {"title": "Doc 2", "content": "Content 2"}
        ]
        
        response = requests.post(
            f"{base_url}{API_PREFIX}/tasks/bulk-process",
            json={
                "task_type": "document_indexing",
                "items": documents
            },
            timeout=TIMEOUT
        )
        
        assert response.status_code == 202
        result = response.json()
        assert "task_id" in result
        
        # 等待任务完成
        task_id = result["task_id"]
        self._wait_for_task(base_url, task_id)
    
    def _wait_for_task(self, base_url: str, task_id: str, timeout: int = 60):
        """等待任务完成"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            response = requests.get(
                f"{base_url}{API_PREFIX}/tasks/{task_id}",
                timeout=TIMEOUT
            )
            
            if response.status_code == 200:
                status = response.json()
                if status["status"] == "completed":
                    return status
                elif status["status"] == "failed":
                    pytest.fail(f"Task failed: {status.get('error')}")
            
            time.sleep(1)
        
        pytest.fail("Task timeout")


class TestDataPersistenceE2E:
    """数据持久化端到端测试"""
    
    def test_validation_history_persistence(self, base_url: str, sample_schema: Dict):
        """验证历史持久化"""
        # 1. 执行验证
        response = requests.post(
            f"{base_url}{API_PREFIX}/validate",
            json={
                "schema": sample_schema,
                "schema_type": "json_schema"
            },
            timeout=TIMEOUT
        )
        
        assert response.status_code == 200
        validation_id = response.json()["validation_id"]
        
        # 2. 验证后可以从历史记录中查询
        time.sleep(2)  # 等待持久化
        
        response = requests.get(
            f"{base_url}{API_PREFIX}/history/validations",
            params={"limit": 10},
            timeout=TIMEOUT
        )
        
        assert response.status_code == 200
        history = response.json()
        assert any(v["validation_id"] == validation_id for v in history.get("items", []))
    
    def test_user_preferences_persistence(self, base_url: str):
        """用户偏好持久化"""
        preferences = {
            "theme": "dark",
            "language": "zh-CN",
            "notifications": {
                "email": True,
                "webhook": False
            }
        }
        
        # 保存偏好
        response = requests.post(
            f"{base_url}{API_PREFIX}/user/preferences",
            json=preferences,
            timeout=TIMEOUT
        )
        
        assert response.status_code == 200
        
        # 验证偏好已保存
        response = requests.get(
            f"{base_url}{API_PREFIX}/user/preferences",
            timeout=TIMEOUT
        )
        
        assert response.status_code == 200
        saved_prefs = response.json()
        assert saved_prefs["theme"] == "dark"


class TestConcurrentOperationsE2E:
    """并发操作端到端测试"""
    
    @pytest.mark.skip(reason="长时间运行")
    def test_concurrent_validations(self, base_url: str, sample_schema: Dict):
        """并发验证测试"""
        import concurrent.futures
        
        def validate():
            response = requests.post(
                f"{base_url}{API_PREFIX}/validate",
                json={
                    "schema": sample_schema,
                    "schema_type": "json_schema"
                },
                timeout=TIMEOUT
            )
            return response.status_code == 200
        
        # 并发执行10个验证请求
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(validate) for _ in range(10)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        # 所有请求都应该成功
        assert all(results), f"Only {sum(results)}/10 requests succeeded"


class TestErrorScenariosE2E:
    """错误场景端到端测试"""
    
    def test_invalid_json_payload(self, base_url: str):
        """无效JSON负载"""
        response = requests.post(
            f"{base_url}{API_PREFIX}/validate",
            data="invalid json {",
            headers={"Content-Type": "application/json"},
            timeout=TIMEOUT
        )
        
        assert response.status_code == 400
    
    def test_missing_required_fields(self, base_url: str):
        """缺少必需字段"""
        response = requests.post(
            f"{base_url}{API_PREFIX}/validate",
            json={"schema_type": "json_schema"},  # 缺少schema字段
            timeout=TIMEOUT
        )
        
        assert response.status_code == 422
        result = response.json()
        assert "detail" in result
    
    def test_nonexistent_resource(self, base_url: str):
        """不存在的资源"""
        response = requests.get(
            f"{base_url}{API_PREFIX}/validate/nonexistent-id",
            timeout=TIMEOUT
        )
        
        assert response.status_code == 404


class TestPerformanceE2E:
    """性能端到端测试"""
    
    def test_response_time(self, base_url: str):
        """响应时间测试"""
        start_time = time.time()
        
        response = requests.get(f"{base_url}/health", timeout=TIMEOUT)
        
        elapsed = time.time() - start_time
        
        assert response.status_code == 200
        assert elapsed < 1.0, f"Response too slow: {elapsed:.2f}s"
    
    def test_large_payload_handling(self, base_url: str):
        """大负载处理测试"""
        # 生成大型schema
        large_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {}
        }
        
        for i in range(100):
            large_schema["properties"][f"field_{i}"] = {
                "type": "string",
                "description": f"Description for field {i}" * 100
            }
        
        response = requests.post(
            f"{base_url}{API_PREFIX}/validate",
            json={
                "schema": large_schema,
                "schema_type": "json_schema"
            },
            timeout=60  # 更长的超时
        )
        
        assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
