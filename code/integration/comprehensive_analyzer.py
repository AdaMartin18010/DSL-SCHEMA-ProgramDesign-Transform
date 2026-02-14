"""
综合分析器和报告生成器

提供综合分析和报告生成功能
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import logging
import json

from .comprehensive_integration_framework import (
    ComprehensiveIntegrationFramework,
    IntegrationResult
)
from .industry_adapter_framework import IndustryAdapterFramework
from .ai_driven_transformation import AIDrivenTransformation

logger = logging.getLogger(__name__)


@dataclass
class ComprehensiveReport:
    """综合分析报告"""
    report_id: str
    timestamp: datetime
    source_schema_name: str
    target_schema_name: str
    integration_result: IntegrationResult
    industry_analysis: Dict[str, Any]
    ai_analysis: Dict[str, Any]
    recommendations: List[str]
    summary: Dict[str, Any]


class ComprehensiveAnalyzer:
    """综合分析器"""
    
    def __init__(
        self,
        integration_framework: Optional[ComprehensiveIntegrationFramework] = None,
        industry_framework: Optional[IndustryAdapterFramework] = None,
        ai_transformation: Optional[AIDrivenTransformation] = None
    ):
        """初始化综合分析器"""
        self.integration_framework = integration_framework or ComprehensiveIntegrationFramework()
        self.industry_framework = industry_framework or IndustryAdapterFramework()
        self.ai_transformation = ai_transformation or AIDrivenTransformation()
        self.reports: List[ComprehensiveReport] = []
    
    def comprehensive_analysis(
        self,
        source_schema: Dict[str, Any],
        target_schema: Dict[str, Any],
        source_schema_name: str = "source",
        target_schema_name: str = "target",
        source_industry: Optional[str] = None,
        target_industry: Optional[str] = None,
        use_ai: bool = False
    ) -> ComprehensiveReport:
        """综合分析"""
        report_id = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 1. 综合整合分析
        integration_result = self.integration_framework.integrate_analysis(
            source_schema, target_schema
        )
        
        # 2. 行业分析
        industry_analysis = {}
        if source_industry and target_industry:
            try:
                industry_analysis = self._analyze_industry_conversion(
                    source_schema, target_schema,
                    source_industry, target_industry
                )
            except Exception as e:
                logger.error(f"行业分析失败: {str(e)}")
                industry_analysis = {"error": str(e)}
        
        # 3. AI分析
        ai_analysis = {}
        if use_ai and self.ai_transformation:
            try:
                ai_result = self.ai_transformation.transform_with_ai(
                    source_schema,
                    source_schema.get("format", "openapi"),
                    target_schema.get("format", "openapi")
                )
                ai_analysis = {
                    "confidence": ai_result.confidence,
                    "execution_time": ai_result.execution_time,
                    "model_used": ai_result.model_used,
                    "success": ai_result.success
                }
            except Exception as e:
                logger.error(f"AI分析失败: {str(e)}")
                ai_analysis = {"error": str(e)}
        
        # 4. 生成建议
        recommendations = self._generate_comprehensive_recommendations(
            integration_result, industry_analysis, ai_analysis
        )
        
        # 5. 生成摘要
        summary = self._generate_summary(
            integration_result, industry_analysis, ai_analysis
        )
        
        # 创建报告
        report = ComprehensiveReport(
            report_id=report_id,
            timestamp=datetime.now(),
            source_schema_name=source_schema_name,
            target_schema_name=target_schema_name,
            integration_result=integration_result,
            industry_analysis=industry_analysis,
            ai_analysis=ai_analysis,
            recommendations=recommendations,
            summary=summary
        )
        
        self.reports.append(report)
        logger.info(f"综合分析完成: {report_id}")
        
        return report
    
    def _analyze_industry_conversion(
        self,
        source_schema: Dict[str, Any],
        target_schema: Dict[str, Any],
        source_industry: str,
        target_industry: str
    ) -> Dict[str, Any]:
        """分析行业转换"""
        # 检查是否有适配器
        adapters = self.industry_framework.get_adapter_list()
        
        source_adapter = next(
            (a for a in adapters if a["industry_type"] == source_industry),
            None
        )
        target_adapter = next(
            (a for a in adapters if a["industry_type"] == target_industry),
            None
        )
        
        return {
            "source_industry": source_industry,
            "target_industry": target_industry,
            "source_adapter_available": source_adapter is not None,
            "target_adapter_available": target_adapter is not None,
            "conversion_feasible": source_adapter is not None and target_adapter is not None,
            "adapter_recommendations": self._recommend_adapters(source_industry, target_industry)
        }
    
    def _recommend_adapters(
        self,
        source_industry: str,
        target_industry: str
    ) -> List[str]:
        """推荐适配器"""
        recommendations = []
        
        if source_industry == "finance":
            recommendations.append("SWIFT适配器")
            recommendations.append("ISO 20022适配器")
        
        if target_industry == "healthcare":
            recommendations.append("FHIR适配器")
        
        return recommendations
    
    def _generate_comprehensive_recommendations(
        self,
        integration_result: IntegrationResult,
        industry_analysis: Dict[str, Any],
        ai_analysis: Dict[str, Any]
    ) -> List[str]:
        """生成综合建议"""
        recommendations = []
        
        # 基于整合结果
        recommendations.extend(integration_result.recommendations)
        
        # 基于行业分析
        if industry_analysis.get("conversion_feasible") is False:
            recommendations.append(
                "跨行业转换不可行，建议使用通用Schema作为中间格式"
            )
        
        # 基于AI分析
        if ai_analysis.get("confidence", 0.0) < 0.8:
            recommendations.append(
                "AI转换置信度较低，建议使用规则引擎进行后处理"
            )
        
        return recommendations
    
    def _generate_summary(
        self,
        integration_result: IntegrationResult,
        industry_analysis: Dict[str, Any],
        ai_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """生成摘要"""
        return {
            "overall_score": integration_result.overall_score,
            "integration_level": integration_result.integration_level.value,
            "dimensions_analyzed": len(integration_result.dimensions),
            "industry_feasible": industry_analysis.get("conversion_feasible", False),
            "ai_confidence": ai_analysis.get("confidence", 0.0),
            "total_recommendations": len(integration_result.recommendations)
        }
    
    def _convert_to_json_serializable(self, obj):
        """将对象转换为JSON可序列化的格式"""
        if isinstance(obj, dict):
            # 处理tuple作为key的情况
            result = {}
            for key, value in obj.items():
                if isinstance(key, tuple):
                    key = "_".join(str(k) for k in key)
                result[key] = self._convert_to_json_serializable(value)
            return result
        elif isinstance(obj, list):
            return [self._convert_to_json_serializable(item) for item in obj]
        elif isinstance(obj, tuple):
            return [self._convert_to_json_serializable(item) for item in obj]
        elif hasattr(obj, 'value'):
            return obj.value
        else:
            return obj
    
    def generate_report(
        self,
        report: ComprehensiveReport,
        format: str = "json"
    ) -> str:
        """生成报告"""
        if format == "json":
            return json.dumps({
                "report_id": report.report_id,
                "timestamp": report.timestamp.isoformat(),
                "source_schema": report.source_schema_name,
                "target_schema": report.target_schema_name,
                "overall_score": report.integration_result.overall_score,
                "integration_level": report.integration_result.integration_level.value,
                "dimensions": [d.value for d in report.integration_result.dimensions],
                "results": self._convert_to_json_serializable(report.integration_result.results),
                "industry_analysis": self._convert_to_json_serializable(report.industry_analysis),
                "ai_analysis": self._convert_to_json_serializable(report.ai_analysis),
                "recommendations": report.recommendations,
                "summary": report.summary
            }, indent=2, ensure_ascii=False)
        else:
            # 文本格式
            lines = [
                f"综合分析报告 ID: {report.report_id}",
                f"时间: {report.timestamp.isoformat()}",
                f"源Schema: {report.source_schema_name}",
                f"目标Schema: {report.target_schema_name}",
                f"总体分数: {report.integration_result.overall_score:.2%}",
                f"整合级别: {report.integration_result.integration_level.value}",
                "",
                "分析维度:",
            ]
            
            for dim in report.integration_result.dimensions:
                lines.append(f"- {dim.value}")
            
            lines.extend([
                "",
                "建议:",
            ])
            
            for i, rec in enumerate(report.recommendations, 1):
                lines.append(f"{i}. {rec}")
            
            return "\n".join(lines)
    
    def get_analysis_statistics(self) -> Dict[str, Any]:
        """获取分析统计信息"""
        total_reports = len(self.reports)
        
        if total_reports == 0:
            return {
                "total_reports": 0,
                "average_score": 0.0
            }
        
        avg_score = sum(
            r.integration_result.overall_score for r in self.reports
        ) / total_reports
        
        return {
            "total_reports": total_reports,
            "average_score": avg_score,
            "integration_framework_stats": self.integration_framework.get_integration_statistics(),
            "industry_framework_stats": self.industry_framework.get_rule_library_summary(),
            "ai_transformation_stats": self.ai_transformation.get_transformation_statistics() if self.ai_transformation else None
        }
