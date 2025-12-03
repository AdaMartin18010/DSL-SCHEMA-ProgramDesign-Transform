"""
快速开始示例

演示如何使用各个核心模块
"""

import asyncio
import httpx
from typing import Dict, Any


"""
快速开始示例

演示如何使用各个核心模块

注意：需要先启动所有服务
- 使用 docker-compose up -d 启动所有服务
- 或使用 python code/scripts/run_all_apis.py 启动所有API服务
"""

# API网关地址
GATEWAY_URL = "http://localhost:8080"


async def example_multimodal_kg():
    """多模态知识图谱示例"""
    print("\n=== 多模态知识图谱示例 ===")
    
    async with httpx.AsyncClient() as client:
        # 添加文本实体
        response = await client.post(
            f"{GATEWAY_URL}/api/v1/multimodal_kg/entity/add",
            json={
                "entity_id": "schema_001",
                "entity_type": "schema",
                "text_content": "This is a payment schema",
                "text_type": "schema_doc"
            }
        )
        print(f"添加文本实体: {response.json()}")
        
        # 搜索相似实体
        response = await client.post(
            f"{GATEWAY_URL}/api/v1/multimodal_kg/search/similar",
            json={
                "query": "payment",
                "top_k": 5
            }
        )
        print(f"相似实体搜索: {response.json()}")


async def example_temporal_kg():
    """时序知识图谱示例"""
    print("\n=== 时序知识图谱示例 ===")
    
    async with httpx.AsyncClient() as client:
        # 添加实体
        response = await client.post(
            f"{GATEWAY_URL}/api/v1/temporal_kg/entity/add",
            json={
                "entity_id": "schema_001",
                "entity_type": "schema",
                "valid_from": "2025-01-01T00:00:00",
                "properties": {"version": "1.0"}
            }
        )
        print(f"添加实体: {response.json()}")
        
        # 查询时间演化
        response = await client.get(
            f"{GATEWAY_URL}/api/v1/temporal_kg/evolution/schema_001"
        )
        print(f"演化历史: {response.json()}")


async def example_usl():
    """统一Schema语言示例"""
    print("\n=== 统一Schema语言示例 ===")
    
    usl_code = """
    schema PaymentSchema {
      field amount: Decimal {
        required: true
        constraint: {
          min: 0
          max: 1000000
        }
      }
    }
    """
    
    async with httpx.AsyncClient() as client:
        # 解析USL
        response = await client.post(
            f"{GATEWAY_URL}/api/v1/usl/parse",
            json={"usl_code": usl_code}
        )
        print(f"USL解析: {response.json()}")
        
        # 验证USL
        response = await client.post(
            f"{GATEWAY_URL}/api/v1/usl/validate",
            json={"usl_code": usl_code}
        )
        print(f"USL验证: {response.json()}")


async def example_hierarchical_kg():
    """层次化知识表示示例"""
    print("\n=== 层次化知识表示示例 ===")
    
    async with httpx.AsyncClient() as client:
        # 添加实例层实体
        response = await client.post(
            f"{GATEWAY_URL}/api/v1/hierarchical_kg/entity/add",
            json={
                "entity_id": "instance_001",
                "name": "Payment Instance",
                "level": 1,
                "content": {"type": "schema_instance"}
            }
        )
        print(f"添加实例: {response.json()}")
        
        # 自底向上推理
        response = await client.post(
            f"{GATEWAY_URL}/api/v1/hierarchical_kg/reasoning",
            json={
                "entity_id": "instance_001",
                "reasoning_type": "bottom_up"
            }
        )
        print(f"推理路径: {response.json()}")


async def example_schema_versioning():
    """Schema版本管理示例"""
    print("\n=== Schema版本管理示例 ===")
    
    async with httpx.AsyncClient() as client:
        # 创建版本
        response = await client.post(
            f"{GATEWAY_URL}/api/v1/schema_versioning/version/create",
            json={
                "schema_id": "payment_schema",
                "schema_content": {
                    "fields": {
                        "amount": {"type": "decimal", "required": True}
                    }
                },
                "version": "1.0.0"
            }
        )
        print(f"创建版本: {response.json()}")
        
        # 检查兼容性
        response = await client.post(
            f"{GATEWAY_URL}/api/v1/schema_versioning/compatibility/check",
            json={
                "schema_id": "payment_schema",
                "from_version": "1.0.0",
                "to_version": "1.1.0"
            }
        )
        print(f"兼容性检查: {response.json()}")


async def main():
    """主函数"""
    print("DSL Schema快速开始示例")
    print("=" * 50)
    
    # 检查网关健康状态
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{GATEWAY_URL}/api/v1/health")
            health = response.json()
            print(f"\n网关状态: {health.get('overall', 'unknown')}")
            print(f"服务状态: {health.get('services', {})}")
        except Exception as e:
            print(f"无法连接到API网关: {e}")
            print("请确保API网关已启动（端口8080）")
            return
    
    # 运行示例
    await example_multimodal_kg()
    await example_temporal_kg()
    await example_usl()
    await example_hierarchical_kg()
    await example_schema_versioning()
    
    print("\n" + "=" * 50)
    print("示例完成！")


if __name__ == "__main__":
    asyncio.run(main())
