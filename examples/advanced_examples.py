"""
高级使用示例

演示更复杂的使用场景
"""

import asyncio
import httpx
from typing import Dict, Any, List


# API网关地址
GATEWAY_URL = "http://localhost:8080"


async def example_multimodal_schema_storage():
    """多模态Schema存储示例"""
    print("\n=== 多模态Schema存储示例 ===")
    
    async with httpx.AsyncClient() as client:
        # 1. 存储Schema文本
        response = await client.post(
            f"{GATEWAY_URL}/api/v1/multimodal_kg/entity/add",
            json={
                "entity_id": "payment_schema_v1",
                "entity_type": "schema",
                "text_content": """
                Payment Schema v1.0
                - amount: decimal
                - currency: string
                - timestamp: datetime
                """,
                "text_type": "schema_doc"
            }
        )
        print(f"存储Schema文本: {response.json()}")
        
        # 2. 存储Schema图像（如果有）
        # response = await client.post(
        #     f"{GATEWAY_URL}/api/v1/multimodal_kg/entity/add",
        #     json={
        #         "entity_id": "payment_schema_v1",
        #         "entity_type": "schema",
        #         "image_url": "https://example.com/schema-diagram.png",
        #         "image_type": "schema_diagram"
        #     }
        # )
        
        # 3. 多模态搜索
        response = await client.post(
            f"{GATEWAY_URL}/api/v1/multimodal_kg/search/similar",
            json={
                "query": "payment transaction",
                "top_k": 10
            }
        )
        print(f"多模态搜索结果: {response.json()}")


async def example_temporal_schema_evolution():
    """时序Schema演化示例"""
    print("\n=== 时序Schema演化示例 ===")
    
    async with httpx.AsyncClient() as client:
        # 1. 创建Schema v1.0
        response = await client.post(
            f"{GATEWAY_URL}/api/v1/temporal_kg/entity/add",
            json={
                "entity_id": "payment_schema",
                "entity_type": "schema",
                "valid_from": "2025-01-01T00:00:00",
                "valid_to": "2025-06-30T23:59:59",
                "properties": {
                    "version": "1.0",
                    "fields": ["amount", "currency"]
                }
            }
        )
        print(f"创建Schema v1.0: {response.json()}")
        
        # 2. 创建Schema v2.0（演化）
        response = await client.post(
            f"{GATEWAY_URL}/api/v1/temporal_kg/entity/add",
            json={
                "entity_id": "payment_schema",
                "entity_type": "schema",
                "valid_from": "2025-07-01T00:00:00",
                "properties": {
                    "version": "2.0",
                    "fields": ["amount", "currency", "timestamp", "status"]
                }
            }
        )
        print(f"创建Schema v2.0: {response.json()}")
        
        # 3. 查询演化历史
        response = await client.get(
            f"{GATEWAY_URL}/api/v1/temporal_kg/evolution/payment_schema"
        )
        print(f"演化历史: {response.json()}")


async def example_usl_schema_conversion():
    """USL Schema转换示例"""
    print("\n=== USL Schema转换示例 ===")
    
    usl_code = """
    schema PaymentSchema {
      field amount: Decimal {
        required: true
        constraint: {
          min: 0
          max: 1000000
        }
      }
      
      field currency: String {
        required: true
        default: "USD"
        enum: ["USD", "EUR", "CNY"]
      }
      
      field timestamp: DateTime {
        required: true
      }
    }
    """
    
    async with httpx.AsyncClient() as client:
        # 1. 解析USL
        response = await client.post(
            f"{GATEWAY_URL}/api/v1/usl/parse",
            json={"usl_code": usl_code}
        )
        ast = response.json()
        print(f"USL解析结果: {ast.get('ast', {})}")
        
        # 2. 验证USL
        response = await client.post(
            f"{GATEWAY_URL}/api/v1/usl/validate",
            json={"usl_code": usl_code}
        )
        validation = response.json()
        print(f"USL验证结果: {validation.get('valid', False)}")
        
        # 3. 转换为OpenAPI
        response = await client.post(
            f"{GATEWAY_URL}/api/v1/usl/convert",
            json={
                "usl_code": usl_code,
                "target_format": "openapi"
            }
        )
        openapi = response.json()
        print(f"OpenAPI转换结果: {openapi.get('openapi', {})}")


async def example_hierarchical_abstraction():
    """层次化抽象示例"""
    print("\n=== 层次化抽象示例 ===")
    
    async with httpx.AsyncClient() as client:
        # 1. 添加多个实例
        instances = ["instance_001", "instance_002", "instance_003"]
        for instance_id in instances:
            response = await client.post(
                f"{GATEWAY_URL}/api/v1/hierarchical_kg/entity/add",
                json={
                    "entity_id": instance_id,
                    "name": f"Payment Instance {instance_id}",
                    "level": 1,
                    "content": {"type": "schema_instance", "domain": "finance"}
                }
            )
            print(f"添加实例 {instance_id}: {response.json()}")
        
        # 2. 抽象为模式
        response = await client.post(
            f"{GATEWAY_URL}/api/v1/hierarchical_kg/abstraction/instances-to-pattern",
            json={"instance_ids": instances}
        )
        pattern = response.json()
        print(f"抽象为模式: {pattern.get('pattern', {})}")
        
        # 3. 自底向上推理
        response = await client.post(
            f"{GATEWAY_URL}/api/v1/hierarchical_kg/reasoning",
            json={
                "entity_id": "instance_001",
                "reasoning_type": "bottom_up"
            }
        )
        reasoning = response.json()
        print(f"推理路径: {reasoning.get('reasoning_path', [])}")


async def example_schema_version_migration():
    """Schema版本迁移示例"""
    print("\n=== Schema版本迁移示例 ===")
    
    async with httpx.AsyncClient() as client:
        # 1. 创建Schema v1.0
        response = await client.post(
            f"{GATEWAY_URL}/api/v1/schema_versioning/version/create",
            json={
                "schema_id": "payment_schema",
                "schema_content": {
                    "fields": {
                        "amount": {"type": "decimal", "required": True},
                        "currency": {"type": "string", "required": True}
                    }
                },
                "version": "1.0.0",
                "changelog": "Initial version"
            }
        )
        print(f"创建版本1.0.0: {response.json()}")
        
        # 2. 创建Schema v2.0
        response = await client.post(
            f"{GATEWAY_URL}/api/v1/schema_versioning/version/create",
            json={
                "schema_id": "payment_schema",
                "schema_content": {
                    "fields": {
                        "amount": {"type": "decimal", "required": True},
                        "currency": {"type": "string", "required": True},
                        "timestamp": {"type": "datetime", "required": True},
                        "status": {"type": "string", "required": False, "default": "pending"}
                    }
                },
                "version": "2.0.0",
                "changelog": "Added timestamp and status fields"
            }
        )
        print(f"创建版本2.0.0: {response.json()}")
        
        # 3. 检查兼容性
        response = await client.post(
            f"{GATEWAY_URL}/api/v1/schema_versioning/compatibility/check",
            json={
                "schema_id": "payment_schema",
                "from_version": "1.0.0",
                "to_version": "2.0.0"
            }
        )
        compatibility = response.json()
        print(f"兼容性检查: {compatibility}")
        
        # 4. 执行迁移
        if compatibility.get('is_compatible', 0) > 0:
            response = await client.post(
                f"{GATEWAY_URL}/api/v1/schema_versioning/migration/migrate",
                json={
                    "schema_id": "payment_schema",
                    "from_version": "1.0.0",
                    "to_version": "2.0.0",
                    "data": {
                        "amount": 100.50,
                        "currency": "USD"
                    }
                }
            )
            migrated = response.json()
            print(f"迁移结果: {migrated}")


async def example_integrated_workflow():
    """集成工作流示例"""
    print("\n=== 集成工作流示例 ===")
    
    async with httpx.AsyncClient() as client:
        # 1. 使用USL定义Schema
        usl_code = """
        schema PaymentSchema {
          field amount: Decimal { required: true }
          field currency: String { required: true }
        }
        """
        
        # 2. 解析和验证USL
        response = await client.post(
            f"{GATEWAY_URL}/api/v1/usl/parse",
            json={"usl_code": usl_code}
        )
        print(f"USL解析: {response.json()}")
        
        # 3. 存储到多模态KG
        response = await client.post(
            f"{GATEWAY_URL}/api/v1/multimodal_kg/entity/add",
            json={
                "entity_id": "payment_schema_usl",
                "entity_type": "schema",
                "text_content": usl_code,
                "text_type": "usl_schema"
            }
        )
        print(f"存储到多模态KG: {response.json()}")
        
        # 4. 记录到时序KG
        response = await client.post(
            f"{GATEWAY_URL}/api/v1/temporal_kg/entity/add",
            json={
                "entity_id": "payment_schema_usl",
                "entity_type": "schema",
                "valid_from": "2025-01-21T00:00:00",
                "properties": {"version": "1.0.0", "source": "usl"}
            }
        )
        print(f"记录到时序KG: {response.json()}")
        
        # 5. 创建版本
        response = await client.post(
            f"{GATEWAY_URL}/api/v1/schema_versioning/version/create",
            json={
                "schema_id": "payment_schema_usl",
                "schema_content": {"usl_code": usl_code},
                "version": "1.0.0"
            }
        )
        print(f"创建版本: {response.json()}")


async def main():
    """主函数"""
    print("DSL Schema高级使用示例")
    print("=" * 50)
    
    # 检查网关健康状态
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{GATEWAY_URL}/api/v1/health")
            health = response.json()
            print(f"\n网关状态: {health.get('overall', 'unknown')}")
        except Exception as e:
            print(f"无法连接到API网关: {e}")
            print("请确保API网关已启动（端口8080）")
            return
    
    # 运行示例
    await example_multimodal_schema_storage()
    await example_temporal_schema_evolution()
    await example_usl_schema_conversion()
    await example_hierarchical_abstraction()
    await example_schema_version_migration()
    await example_integrated_workflow()
    
    print("\n" + "=" * 50)
    print("高级示例完成！")


if __name__ == "__main__":
    asyncio.run(main())
