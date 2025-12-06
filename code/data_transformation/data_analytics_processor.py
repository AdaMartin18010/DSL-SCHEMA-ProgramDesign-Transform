"""
数据分析处理器

专注于数据分析相关的处理
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class AnalysisType(Enum):
    """分析类型"""
    STATISTICAL = "statistical"  # 统计分析
    PREDICTIVE = "predictive"  # 预测分析
    DESCRIPTIVE = "descriptive"  # 描述性分析
    DIAGNOSTIC = "diagnostic"  # 诊断分析
    PRESCRIPTIVE = "prescriptive"  # 规范性分析


@dataclass
class AnalysisRule:
    """分析规则"""
    rule_id: str
    analysis_type: AnalysisType
    data_sources: List[str]  # 数据源
    metrics: List[str]  # 指标
    dimensions: List[str]  # 维度
    filters: Optional[Dict[str, Any]] = None  # 过滤条件
    aggregation: Optional[Dict[str, Any]] = None  # 聚合配置


@dataclass
class AnalysisResult:
    """分析结果"""
    result_id: str
    rule_id: str
    analysis_type: AnalysisType
    data: List[Dict[str, Any]]  # 分析数据
    metrics: Dict[str, Any]  # 指标值
    insights: List[str]  # 洞察
    timestamp: datetime


class DataAnalyticsProcessor:
    """
    数据分析处理器
    
    专注于数据分析处理
    """
    
    def __init__(self):
        self.analysis_rules: Dict[str, AnalysisRule] = {}
        self.analysis_results: List[AnalysisResult] = []
    
    def create_analysis_rule(self, rule_config: Dict[str, Any]) -> AnalysisRule:
        """
        创建分析规则
        
        Args:
            rule_config: 规则配置
            
        Returns:
            分析规则对象
        """
        rule_id = rule_config.get('rule_id', f"analysis_{datetime.utcnow().timestamp()}")
        
        rule = AnalysisRule(
            rule_id=rule_id,
            analysis_type=AnalysisType(rule_config.get('analysis_type', 'statistical')),
            data_sources=rule_config.get('data_sources', []),
            metrics=rule_config.get('metrics', []),
            dimensions=rule_config.get('dimensions', []),
            filters=rule_config.get('filters'),
            aggregation=rule_config.get('aggregation')
        )
        
        self.analysis_rules[rule_id] = rule
        return rule
    
    def execute_analysis(self, rule_id: str,
                        data: Optional[List[Dict[str, Any]]] = None) -> AnalysisResult:
        """
        执行分析
        
        Args:
            rule_id: 规则ID
            data: 输入数据（可选）
            
        Returns:
            分析结果
        """
        if rule_id not in self.analysis_rules:
            raise ValueError(f'规则不存在: {rule_id}')
        
        rule = self.analysis_rules[rule_id]
        
        # 根据分析类型执行不同的分析
        if rule.analysis_type == AnalysisType.STATISTICAL:
            result_data, metrics = self._statistical_analysis(rule, data)
        elif rule.analysis_type == AnalysisType.PREDICTIVE:
            result_data, metrics = self._predictive_analysis(rule, data)
        elif rule.analysis_type == AnalysisType.DESCRIPTIVE:
            result_data, metrics = self._descriptive_analysis(rule, data)
        elif rule.analysis_type == AnalysisType.DIAGNOSTIC:
            result_data, metrics = self._diagnostic_analysis(rule, data)
        elif rule.analysis_type == AnalysisType.PRESCRIPTIVE:
            result_data, metrics = self._prescriptive_analysis(rule, data)
        else:
            result_data, metrics = [], {}
        
        # 生成洞察
        insights = self._generate_insights(rule, metrics)
        
        result = AnalysisResult(
            result_id=f"result_{datetime.utcnow().timestamp()}",
            rule_id=rule_id,
            analysis_type=rule.analysis_type,
            data=result_data,
            metrics=metrics,
            insights=insights,
            timestamp=datetime.utcnow()
        )
        
        self.analysis_results.append(result)
        return result
    
    def _statistical_analysis(self, rule: AnalysisRule,
                             data: Optional[List[Dict[str, Any]]]) -> tuple:
        """统计分析"""
        if not data:
            return [], {}
        
        metrics = {}
        
        # 计算基本统计量
        for metric in rule.metrics:
            values = [record.get(metric) for record in data if metric in record]
            values = [v for v in values if v is not None and isinstance(v, (int, float))]
            
            if values:
                metrics[metric] = {
                    'count': len(values),
                    'sum': sum(values),
                    'mean': sum(values) / len(values),
                    'min': min(values),
                    'max': max(values),
                    'std': self._calculate_std(values)
                }
        
        # 按维度聚合
        result_data = []
        if rule.dimensions:
            dimension_groups = {}
            for record in data:
                key = tuple(record.get(dim) for dim in rule.dimensions)
                if key not in dimension_groups:
                    dimension_groups[key] = []
                dimension_groups[key].append(record)
            
            for key, group in dimension_groups.items():
                aggregated = {rule.dimensions[i]: key[i] for i in range(len(rule.dimensions))}
                
                for metric in rule.metrics:
                    values = [r.get(metric) for r in group if metric in r]
                    values = [v for v in values if v is not None and isinstance(v, (int, float))]
                    
                    if values:
                        aggregated[f"{metric}_sum"] = sum(values)
                        aggregated[f"{metric}_avg"] = sum(values) / len(values)
                        aggregated[f"{metric}_count"] = len(values)
                
                result_data.append(aggregated)
        else:
            result_data = data
        
        return result_data, metrics
    
    def _predictive_analysis(self, rule: AnalysisRule,
                            data: Optional[List[Dict[str, Any]]]) -> tuple:
        """预测分析"""
        # 简化实现
        return [], {}
    
    def _descriptive_analysis(self, rule: AnalysisRule,
                             data: Optional[List[Dict[str, Any]]]) -> tuple:
        """描述性分析"""
        # 简化实现
        return self._statistical_analysis(rule, data)
    
    def _diagnostic_analysis(self, rule: AnalysisRule,
                           data: Optional[List[Dict[str, Any]]]) -> tuple:
        """诊断分析"""
        # 简化实现
        return [], {}
    
    def _prescriptive_analysis(self, rule: AnalysisRule,
                              data: Optional[List[Dict[str, Any]]]) -> tuple:
        """规范性分析"""
        # 简化实现
        return [], {}
    
    def _calculate_std(self, values: List[float]) -> float:
        """计算标准差"""
        if not values:
            return 0.0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance ** 0.5
    
    def _generate_insights(self, rule: AnalysisRule,
                          metrics: Dict[str, Any]) -> List[str]:
        """生成洞察"""
        insights = []
        
        for metric, stats in metrics.items():
            if 'mean' in stats:
                mean = stats['mean']
                std = stats.get('std', 0)
                
                if std > 0:
                    cv = std / mean  # 变异系数
                    if cv > 0.5:
                        insights.append(f"{metric} 的变异系数较高 ({cv:.2f})，数据波动较大")
                    elif cv < 0.1:
                        insights.append(f"{metric} 的变异系数较低 ({cv:.2f})，数据相对稳定")
        
        return insights
    
    def get_analysis_results(self, rule_id: Optional[str] = None,
                            limit: int = 100) -> List[AnalysisResult]:
        """
        获取分析结果
        
        Args:
            rule_id: 规则ID（可选）
            limit: 返回数量限制
            
        Returns:
            分析结果列表
        """
        results = self.analysis_results
        
        if rule_id:
            results = [r for r in results if r.rule_id == rule_id]
        
        return sorted(results, key=lambda x: x.timestamp, reverse=True)[:limit]


def main():
    """主函数 - 示例用法"""
    processor = DataAnalyticsProcessor()
    
    # 创建分析规则
    rule_config = {
        'rule_id': 'sales_analysis',
        'analysis_type': 'statistical',
        'data_sources': ['sales_data'],
        'metrics': ['amount', 'quantity'],
        'dimensions': ['region', 'product_category'],
        'filters': {
            'date_range': {'start': '2024-01-01', 'end': '2024-12-31'}
        }
    }
    
    rule = processor.create_analysis_rule(rule_config)
    print(f"创建分析规则: {rule.rule_id}")
    
    # 示例数据
    sample_data = [
        {'region': 'North', 'product_category': 'Electronics', 'amount': 1000, 'quantity': 10},
        {'region': 'South', 'product_category': 'Electronics', 'amount': 1500, 'quantity': 15},
        {'region': 'North', 'product_category': 'Clothing', 'amount': 800, 'quantity': 20},
    ]
    
    # 执行分析
    result = processor.execute_analysis(rule.rule_id, sample_data)
    print(f"分析结果: {result.result_id}")
    print(f"指标: {result.metrics}")
    print(f"洞察: {result.insights}")


if __name__ == '__main__':
    main()
