"""
数据质量监控模块

专注于数据质量实时监控、质量指标追踪、质量告警
"""

from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import logging
import threading

logger = logging.getLogger(__name__)


class QualityMetric(Enum):
    """质量指标"""
    COMPLETENESS = "completeness"  # 完整性
    ACCURACY = "accuracy"  # 准确性
    CONSISTENCY = "consistency"  # 一致性
    VALIDITY = "validity"  # 有效性
    TIMELINESS = "timeliness"  # 及时性
    UNIQUENESS = "uniqueness"  # 唯一性


class AlertLevel(Enum):
    """告警级别"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class QualityRule:
    """质量规则"""
    rule_id: str
    metric: QualityMetric
    threshold: float
    field: Optional[str] = None
    condition: Optional[Callable[[Dict[str, Any]], bool]] = None


@dataclass
class QualityMetricValue:
    """质量指标值"""
    metric: QualityMetric
    value: float
    timestamp: datetime
    field: Optional[str] = None


@dataclass
class QualityAlert:
    """质量告警"""
    alert_id: str
    rule_id: str
    level: AlertLevel
    message: str
    metric_value: float
    threshold: float
    timestamp: datetime


class DataQualityMonitor:
    """
    数据质量监控器
    
    专注于数据质量实时监控、质量指标追踪、质量告警
    """
    
    def __init__(self):
        self.rules: Dict[str, QualityRule] = {}
        self.metric_history: Dict[str, List[QualityMetricValue]] = {}
        self.alerts: List[QualityAlert] = []
        self.monitoring_active = False
        self.monitoring_thread: Optional[threading.Thread] = None
    
    def add_rule(self, rule_config: Dict[str, Any]) -> QualityRule:
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
            metric=QualityMetric(rule_config.get('metric', 'completeness')),
            threshold=rule_config.get('threshold', 0.9),
            field=rule_config.get('field'),
            condition=rule_config.get('condition')
        )
        
        self.rules[rule_id] = rule
        return rule
    
    def check_quality(self, data: List[Dict[str, Any]], rule_ids: Optional[List[str]] = None) -> Dict[str, float]:
        """
        检查数据质量
        
        Args:
            data: 数据列表
            rule_ids: 规则ID列表（可选）
            
        Returns:
            质量指标值字典
        """
        rules_to_check = rule_ids if rule_ids else list(self.rules.keys())
        metrics = {}
        
        for rule_id in rules_to_check:
            if rule_id not in self.rules:
                continue
            
            rule = self.rules[rule_id]
            metric_value = self._compute_metric(data, rule)
            metrics[rule_id] = metric_value
            
            # 记录指标值
            metric_key = f"{rule.metric.value}_{rule.field or 'all'}"
            if metric_key not in self.metric_history:
                self.metric_history[metric_key] = []
            
            self.metric_history[metric_key].append(
                QualityMetricValue(
                    metric=rule.metric,
                    value=metric_value,
                    timestamp=datetime.utcnow(),
                    field=rule.field
                )
            )
            
            # 检查告警
            if metric_value < rule.threshold:
                self._trigger_alert(rule, metric_value)
        
        return metrics
    
    def _compute_metric(self, data: List[Dict[str, Any]], rule: QualityRule) -> float:
        """计算质量指标"""
        if not data:
            return 0.0
        
        metric = rule.metric
        
        if metric == QualityMetric.COMPLETENESS:
            # 完整性：非空字段比例
            if rule.field:
                non_null_count = sum(1 for r in data if r.get(rule.field) is not None)
                return non_null_count / len(data)
            else:
                # 所有字段的完整性
                total_fields = len(data[0].keys()) if data else 0
                if total_fields == 0:
                    return 0.0
                non_null_total = sum(
                    sum(1 for r in data if r.get(field) is not None)
                    for field in data[0].keys()
                )
                return non_null_total / (len(data) * total_fields)
        
        elif metric == QualityMetric.UNIQUENESS:
            # 唯一性：唯一值比例
            if rule.field:
                unique_values = len(set(r.get(rule.field) for r in data if r.get(rule.field) is not None))
                total_values = sum(1 for r in data if r.get(rule.field) is not None)
                return unique_values / total_values if total_values > 0 else 0.0
            else:
                return 1.0  # 简化实现
        
        elif metric == QualityMetric.VALIDITY:
            # 有效性：满足条件的记录比例
            if rule.condition:
                valid_count = sum(1 for r in data if rule.condition(r))
                return valid_count / len(data)
            else:
                return 1.0
        
        elif metric == QualityMetric.CONSISTENCY:
            # 一致性：简化实现
            return 1.0
        
        elif metric == QualityMetric.ACCURACY:
            # 准确性：简化实现
            return 1.0
        
        elif metric == QualityMetric.TIMELINESS:
            # 及时性：简化实现
            return 1.0
        
        return 1.0
    
    def _trigger_alert(self, rule: QualityRule, metric_value: float):
        """触发告警"""
        # 确定告警级别
        if metric_value < rule.threshold * 0.5:
            level = AlertLevel.CRITICAL
        elif metric_value < rule.threshold * 0.7:
            level = AlertLevel.ERROR
        elif metric_value < rule.threshold * 0.9:
            level = AlertLevel.WARNING
        else:
            level = AlertLevel.INFO
        
        alert = QualityAlert(
            alert_id=f"alert_{datetime.utcnow().timestamp()}",
            rule_id=rule.rule_id,
            level=level,
            message=f"质量指标 {rule.metric.value} 低于阈值: {metric_value:.2f} < {rule.threshold:.2f}",
            metric_value=metric_value,
            threshold=rule.threshold,
            timestamp=datetime.utcnow()
        )
        
        self.alerts.append(alert)
        logger.warning(f"质量告警: {alert.message}")
    
    def get_quality_summary(self, metric_key: Optional[str] = None) -> Dict[str, Any]:
        """
        获取质量摘要
        
        Args:
            metric_key: 指标键（可选）
            
        Returns:
            质量摘要
        """
        if metric_key:
            if metric_key not in self.metric_history:
                return {'error': '指标不存在'}
            
            history = self.metric_history[metric_key]
            if not history:
                return {'error': '没有历史数据'}
            
            values = [m.value for m in history]
            return {
                'metric_key': metric_key,
                'current_value': values[-1],
                'average_value': sum(values) / len(values),
                'min_value': min(values),
                'max_value': max(values),
                'data_points': len(values)
            }
        else:
            return {
                'total_rules': len(self.rules),
                'total_alerts': len(self.alerts),
                'metrics_tracked': len(self.metric_history),
                'recent_alerts': [
                    {
                        'alert_id': a.alert_id,
                        'level': a.level.value,
                        'message': a.message,
                        'timestamp': a.timestamp.isoformat()
                    }
                    for a in self.alerts[-10:]  # 最近10条告警
                ]
            }


def main():
    """主函数 - 示例用法"""
    monitor = DataQualityMonitor()
    
    # 添加质量规则
    rule = monitor.add_rule({
        'metric': 'completeness',
        'field': 'name',
        'threshold': 0.9
    })
    
    # 检查质量
    data = [
        {'id': 1, 'name': 'Alice', 'age': 25},
        {'id': 2, 'name': None, 'age': 30},  # 缺失name
        {'id': 3, 'name': 'Charlie', 'age': 35}
    ]
    
    metrics = monitor.check_quality(data, [rule.rule_id])
    print(f"质量指标: {metrics}")


if __name__ == '__main__':
    main()
