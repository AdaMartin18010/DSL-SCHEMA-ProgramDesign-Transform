"""
综合整合系统使用示例

演示如何使用综合整合框架进行多维度分析和转换
"""

from typing import Dict, Any
import json

# 导入综合整合模块
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from integration import (
    ComprehensiveIntegrationFramework,
    AnalysisDimension,
    IntegrationLevel,
    IndustryAdapterFramework,
    IndustryType,
    SchemaFormat,
    AIDrivenTransformation,
    AIModel,
    PromptStrategy,
    ComprehensiveAnalyzer
)


def example_comprehensive_integration():
    """综合整合示例"""
    print("=" * 60)
    print("综合整合系统使用示例")
    print("=" * 60)
    
    # 1. 创建综合整合框架
    framework = ComprehensiveIntegrationFramework()
    
    # 2. 准备源Schema和目标Schema
    source_schema = {
        "openapi": "3.1.0",
        "info": {
            "title": "User API",
            "version": "1.0.0"
        },
        "paths": {
            "/users": {
                "get": {
                    "summary": "Get users",
                    "responses": {
                        "200": {
                            "description": "Success",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "id": {"type": "integer"},
                                                "name": {"type": "string"}
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    
    target_schema = {
        "asyncapi": "3.0.0",
        "info": {
            "title": "User Events",
            "version": "1.0.0"
        },
        "channels": {
            "user.events": {
                "subscribe": {
                    "message": {
                        "payload": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "integer"},
                                "name": {"type": "string"}
                            }
                        }
                    }
                }
            }
        }
    }
    
    # 3. 执行综合整合分析
    print("\n1. 执行综合整合分析...")
    result = framework.integrate_analysis(
        source_schema=source_schema,
        target_schema=target_schema,
        dimensions=[
            AnalysisDimension.INFORMATION_THEORY,
            AnalysisDimension.FORMAL_LANGUAGE,
            AnalysisDimension.KNOWLEDGE_GRAPH,
            AnalysisDimension.MULTI_DIMENSIONAL,
            AnalysisDimension.PRACTICAL
        ],
        integration_level=IntegrationLevel.COMPREHENSIVE
    )
    
    print(f"   整合ID: {result.integration_id}")
    print(f"   总体分数: {result.overall_score:.2%}")
    print(f"   整合级别: {result.integration_level.value}")
    print(f"   分析维度: {[d.value for d in result.dimensions]}")
    
    # 4. 显示分析结果
    print("\n2. 分析结果详情:")
    if "information_theory" in result.results:
        info_result = result.results["information_theory"]
        if "correctness" in info_result:
            print(f"   信息论正确性: {info_result['correctness']:.2%}")
            print(f"   互信息: {info_result.get('mutual_information', 0):.2f}")
            print(f"   是否无损: {info_result.get('is_lossless', False)}")
    
    if "knowledge_graph" in result.results:
        kg_result = result.results["knowledge_graph"]
        print(f"   知识图谱相似度: {kg_result.get('overall_similarity', 0):.2%}")
    
    # 5. 显示建议
    print("\n3. 优化建议:")
    for i, rec in enumerate(result.recommendations, 1):
        print(f"   {i}. {rec}")
    
    # 6. 创建知识矩阵
    print("\n4. 创建知识矩阵...")
    matrix = framework.create_knowledge_matrix(
        matrix_id="schema_conversion_matrix",
        dimensions=["schema_type", "conversion_direction", "application_domain"],
        values={
            ("openapi", "to_asyncapi", "api"): {"feasibility": "high", "accuracy": 0.95},
            ("asyncapi", "to_openapi", "api"): {"feasibility": "high", "accuracy": 0.90},
            ("iot", "to_openapi", "iot"): {"feasibility": "medium", "accuracy": 0.85}
        }
    )
    print(f"   知识矩阵ID: {matrix.matrix_id}")
    print(f"   维度: {matrix.dimensions}")
    
    # 7. 查询知识矩阵
    print("\n5. 查询知识矩阵...")
    query_results = framework.query_knowledge_matrix(
        matrix_id="schema_conversion_matrix",
        dimension_values={"schema_type": "openapi"}
    )
    print(f"   查询结果数: {len(query_results)}")
    
    return result


def example_industry_adapter():
    """行业适配器示例"""
    print("\n" + "=" * 60)
    print("行业适配器框架使用示例")
    print("=" * 60)
    
    # 1. 创建行业适配器框架
    framework = IndustryAdapterFramework()
    
    # 2. 注册适配器函数
    def swift_to_universal(schema: Dict[str, Any]) -> Dict[str, Any]:
        """SWIFT到通用Schema转换"""
        return {
            "type": "object",
            "properties": schema.get("fields", {})
        }
    
    def universal_to_openapi(schema: Dict[str, Any]) -> Dict[str, Any]:
        """通用Schema到OpenAPI转换"""
        return {
            "openapi": "3.1.0",
            "info": {"title": "Converted API", "version": "1.0.0"},
            "paths": {},
            "components": {"schemas": schema.get("properties", {})}
        }
    
    def validate_swift(schema: Dict[str, Any]) -> bool:
        """验证SWIFT Schema"""
        return "fields" in schema or "message_type" in schema
    
    # 3. 注册适配器
    print("\n1. 注册行业适配器...")
    adapter = framework.register_adapter(
        industry_type=IndustryType.FINANCE,
        source_format=SchemaFormat.SWIFT,
        target_format=SchemaFormat.OPENAPI,
        to_universal_func=swift_to_universal,
        from_universal_func=universal_to_openapi,
        validate_func=validate_swift
    )
    print(f"   适配器ID: {adapter.adapter_id}")
    
    # 4. 添加转换规则
    print("\n2. 添加转换规则...")
    rule = framework.add_conversion_rule(
        rule_name="SWIFT字段到OpenAPI属性",
        rule_type="type_mapping",
        source_pattern={"type": "swift_field", "format": "fixed"},
        target_pattern={"type": "string", "format": "string"},
        priority=1
    )
    print(f"   规则ID: {rule.rule_id}")
    print(f"   规则名称: {rule.rule_name}")
    
    # 5. 获取适配器列表
    print("\n3. 适配器列表:")
    adapters = framework.get_adapter_list()
    for adapter_info in adapters:
        print(f"   - {adapter_info['adapter_id']}: "
              f"{adapter_info['source_format']} -> {adapter_info['target_format']}")
    
    # 6. 获取规则库摘要
    print("\n4. 规则库摘要:")
    summary = framework.get_rule_library_summary()
    print(f"   总规则数: {summary['total_rules']}")
    print(f"   按类型分类: {summary['rules_by_type']}")
    print(f"   启用规则数: {summary['enabled_rules']}")


def example_ai_transformation():
    """AI驱动转换示例"""
    print("\n" + "=" * 60)
    print("AI驱动转换系统使用示例")
    print("=" * 60)
    
    # 1. 创建AI驱动转换系统
    ai_system = AIDrivenTransformation()
    
    # 2. 创建提示模板
    print("\n1. 创建提示模板...")
    template = ai_system.create_prompt_template(
        template_name="OpenAPI到AsyncAPI转换",
        source_format="openapi",
        target_format="asyncapi",
        template="""将以下OpenAPI规范转换为AsyncAPI规范：

源Schema：
{source_format}

要求：
{requirements}

示例：
{examples}

请输出转换后的AsyncAPI规范。""",
        strategy=PromptStrategy.FEW_SHOT,
        examples=[
            {
                "source": {"type": "object", "properties": {"id": {"type": "integer"}}},
                "target": {"type": "object", "properties": {"id": {"type": "integer"}}}
            }
        ]
    )
    print(f"   模板ID: {template.template_id}")
    print(f"   模板名称: {template.template_name}")
    
    # 3. 准备Schema
    source_schema = {
        "openapi": "3.1.0",
        "info": {"title": "Test API", "version": "1.0.0"},
        "paths": {}
    }
    
    # 4. 执行AI转换（模拟）
    print("\n2. 执行AI转换...")
    print("   注意：这是模拟实现，实际需要配置AI模型API密钥")
    
    # 5. 获取转换统计
    print("\n3. 转换统计:")
    stats = ai_system.get_transformation_statistics()
    print(f"   总转换次数: {stats['total_transformations']}")
    print(f"   成功率: {stats['success_rate']:.2%}")
    print(f"   平均置信度: {stats['average_confidence']:.2%}")


def example_comprehensive_analyzer():
    """综合分析器示例"""
    print("\n" + "=" * 60)
    print("综合分析器使用示例")
    print("=" * 60)
    
    # 1. 创建综合分析器
    analyzer = ComprehensiveAnalyzer()
    
    # 2. 准备Schema
    source_schema = {
        "openapi": "3.1.0",
        "info": {"title": "Source API", "version": "1.0.0"},
        "paths": {}
    }
    
    target_schema = {
        "asyncapi": "3.0.0",
        "info": {"title": "Target API", "version": "1.0.0"},
        "channels": {}
    }
    
    # 3. 执行综合分析
    print("\n1. 执行综合分析...")
    report = analyzer.comprehensive_analysis(
        source_schema=source_schema,
        target_schema=target_schema,
        source_schema_name="Source API",
        target_schema_name="Target API",
        source_industry="finance",
        target_industry="api",
        use_ai=False
    )
    
    print(f"   报告ID: {report.report_id}")
    print(f"   总体正确性: {report.integration_result.overall_score:.2%}")
    print(f"   整合级别: {report.integration_result.integration_level.value}")
    
    # 4. 生成报告
    print("\n2. 生成JSON格式报告...")
    json_report = analyzer.generate_report(report, format="json")
    print(f"   报告长度: {len(json_report)} 字符")
    
    print("\n3. 生成文本格式报告...")
    text_report = analyzer.generate_report(report, format="text")
    print(text_report[:500] + "..." if len(text_report) > 500 else text_report)
    
    # 5. 获取分析统计
    print("\n4. 分析统计:")
    stats = analyzer.get_analysis_statistics()
    print(f"   总报告数: {stats['total_reports']}")
    print(f"   平均分数: {stats['average_score']:.2%}")


if __name__ == "__main__":
    # 运行所有示例
    try:
        example_comprehensive_integration()
        example_industry_adapter()
        example_ai_transformation()
        example_comprehensive_analyzer()
        
        print("\n" + "=" * 60)
        print("所有示例运行完成！")
        print("=" * 60)
    except Exception as e:
        print(f"\n示例运行出错: {str(e)}")
        import traceback
        traceback.print_exc()
