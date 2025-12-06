"""
数据质量评估器

专注于数据质量评估和监控
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class QualityDimension(Enum):
    """质量维度"""
    COMPLETENESS = "completeness"  # 完整性
    ACCURACY = "accuracy"  # 准确性
    CONSISTENCY = "consistency"  # 一致性
    VALIDITY = "validity"  # 有效性
    TIMELINESS = "timeliness"  # 及时性
    UNIQUENESS = "uniqueness"  # 唯一性


@dataclass
class QualityRule:
    """质量规则"""
    rule_id: str
    dimension: QualityDimension
    field: str
    rule_type: str  # 规则类型
    rule_config: Dict[str, Any]
    threshold: float = 0.95  # 阈值


@dataclass
class QualityMetric:
    """质量指标"""
    metric_id: str
    dimension: QualityDimension
    field: str
    value: float
    threshold: float
    status: str  # pass, warning, fail
    timestamp: datetime


@dataclass
class QualityAssessment:
    """质量评估"""
    assessment_id: str
    asset_id: str
    overall_score: float
    dimension_scores: Dict[str, float]
    metrics: List[QualityMetric]
    timestamp: datetime


class DataQualityAssessor:
    """
    数据质量评估器
    
    专注于数据质量评估和监控
    """
    
    def __init__(self):
        self.rules: Dict[str, QualityRule] = {}
        self.assessments: Dict[str, QualityAssessment] = {}
    
    def add_quality_rule(self, rule_config: Dict[str, Any]) -> QualityRule:
        """
        添加质量规则
        
        Args:
            rule_config: 规则配置
            
        Returns:
            质量规则对象
        """
        rule_id = rule_config.get('rule_id', f"rule_{datetime.utcnow().timestamp()}")
        
        rule = QualityRule(
            rule_id=rule_id,
            dimension=QualityDimension(rule_config.get('dimension', 'completeness')),
            field=rule_config.get('field', ''),
            rule_type=rule_config.get('rule_type', 'not_null'),
            rule_config=rule_config.get('rule_config', {}),
            threshold=rule_config.get('threshold', 0.95)
        )
        
        self.rules[rule_id] = rule
        return rule
    
    def assess_data_quality(self, asset_id: str, data: List[Dict[str, Any]],
                           rules: Optional[List[str]] = None) -> QualityAssessment:
        """
        评估数据质量
        
        Args:
            asset_id: 资产ID
            data: 数据列表
            rules: 规则ID列表（可选，默认使用所有规则）
            
        Returns:
            质量评估结果
        """
        assessment_id = f"assessment_{datetime.utcnow().timestamp()}"
        
        # 获取要使用的规则
        rules_to_use = rules if rules else list(self.rules.keys())
        
        metrics = []
        dimension_scores = {}
        
        # 按维度分组规则
        dimension_rules = {}
        for rule_id in rules_to_use:
            if rule_id not in self.rules:
                continue
            
            rule = self.rules[rule_id]
            if rule.dimension not in dimension_rules:
                dimension_rules[rule.dimension] = []
            dimension_rules[rule.dimension].append(rule)
        
        # 评估每个维度
        for dimension, rules_list in dimension_rules.items():
            dimension_score, dimension_metrics = self._assess_dimension(
                dimension, rules_list, data
            )
            dimension_scores[dimension.value] = dimension_score
            metrics.extend(dimension_metrics)
        
        # 计算总体分数（加权平均）
        overall_score = sum(dimension_scores.values()) / len(dimension_scores) if dimension_scores else 0.0
        
        assessment = QualityAssessment(
            assessment_id=assessment_id,
            asset_id=asset_id,
            overall_score=overall_score,
            dimension_scores=dimension_scores,
            metrics=metrics,
            timestamp=datetime.utcnow()
        )
        
        self.assessments[assessment_id] = assessment
        return assessment
    
    def _assess_dimension(self, dimension: QualityDimension,
                         rules: List[QualityRule],
                         data: List[Dict[str, Any]]) -> tuple:
        """评估单个维度"""
        if not data:
            return 0.0, []
        
        total_records = len(data)
        passed_records = 0
        metrics = []
        
        for rule in rules:
            field = rule.field
            rule_type = rule.rule_type
            
            # 根据规则类型评估
            if rule_type == 'not_null':
                # 非空检查
                null_count = sum(1 for record in data if field not in record or record[field] is None)
                pass_count = total_records - null_count
                score = pass_count / total_records if total_records > 0 else 0.0
                
            elif rule_type == 'range':
                # 范围检查
                min_val = rule.rule_config.get('min')
                max_val = rule.rule_config.get('max')
                pass_count = sum(
                    1 for record in data
                    if field in record and record[field] is not None
                    and (min_val is None or record[field] >= min_val)
                    and (max_val is None or record[field] <= max_val)
                )
                score = pass_count / total_records if total_records > 0 else 0.0
                
            elif rule_type == 'format':
                # 格式检查
                pattern = rule.rule_config.get('pattern', '')
                pass_count = sum(
                    1 for record in data
                    if field in record and record[field] is not None
                    and self._check_format(record[field], pattern)
                )
                score = pass_count / total_records if total_records > 0 else 0.0
                
            elif rule_type == 'unique':
                # 唯一性检查
                values = [record.get(field) for record in data if field in record]
                unique_count = len(set(values))
                total_count = len(values)
                score = unique_count / total_count if total_count > 0 else 0.0
                
            else:
                score = 1.0
            
            # 确定状态
            status = 'pass' if score >= rule.threshold else 'fail'
            if score < rule.threshold * 0.8:
                status = 'fail'
            elif score < rule.threshold:
                status = 'warning'
            
            metric = QualityMetric(
                metric_id=f"metric_{datetime.utcnow().timestamp()}_{len(metrics)}",
                dimension=dimension,
                field=field,
                value=score,
                threshold=rule.threshold,
                status=status,
                timestamp=datetime.utcnow()
            )
            
            metrics.append(metric)
            passed_records += pass_count if rule_type in ['not_null', 'range', 'format'] else 0
        
        # 计算维度分数
        dimension_score = passed_records / (total_records * len(rules)) if rules and total_records > 0 else 0.0
        
        return dimension_score, metrics
    
    def _check_format(self, value: Any, pattern: str) -> bool:
        """检查格式"""
        import re
        try:
            return bool(re.match(pattern, str(value)))
        except:
            return False
    
    def get_quality_trends(self, asset_id: str, days: int = 30) -> Dict[str, Any]:
        """
        获取质量趋势
        
        Args:
            asset_id: 资产ID
            days: 天数
            
        Returns:
            质量趋势数据
        """
        cutoff_date = datetime.utcnow().replace(day=datetime.utcnow().day - days)
        
        relevant_assessments = [
            a for a in self.assessments.values()
            if a.asset_id == asset_id and a.timestamp >= cutoff_date
        ]
        
        if not relevant_assessments:
            return {
                'asset_id': asset_id,
                'trends': [],
                'average_score': 0.0
            }
        
        # 按时间排序
        relevant_assessments.sort(key=lambda x: x.timestamp)
        
        trends = [
            {
                'timestamp': a.timestamp.isoformat(),
                'overall_score': a.overall_score,
                'dimension_scores': a.dimension_scores
            }
            for a in relevant_assessments
        ]
        
        average_score = sum(a.overall_score for a in relevant_assessments) / len(relevant_assessments)
        
        return {
            'asset_id': asset_id,
            'trends': trends,
            'average_score': average_score,
            'total_assessments': len(relevant_assessments)
        }


def main():
    """主函数 - 示例用法"""
    assessor = DataQualityAssessor()
    
    # 添加质量规则
    rule1 = assessor.add_quality_rule({
        'dimension': 'completeness',
        'field': 'customer_id',
        'rule_type': 'not_null',
        'threshold': 0.95
    })
    
    rule2 = assessor.add_quality_rule({
        'dimension': 'validity',
        'field': 'amount',
        'rule_type': 'range',
        'rule_config': {'min': 0, 'max': 1000000},
        'threshold': 0.98
    })
    
    # 评估数据质量
    sample_data = [
        {'customer_id': 1, 'amount': 1000},
        {'customer_id': 2, 'amount': 2000},
        {'customer_id': None, 'amount': 3000},  # 质量问题
        {'customer_id': 4, 'amount': -100},  # 质量问题
    ]
    
    assessment = assessor.assess_data_quality('asset_1', sample_data)
    print(f"质量评估: 总体分数 {assessment.overall_score:.2%}")
    print(f"维度分数: {assessment.dimension_scores}")


if __name__ == '__main__':
    main()
