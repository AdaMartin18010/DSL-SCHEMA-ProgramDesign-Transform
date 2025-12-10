"""
数据转换监控模块

专注于数据转换监控、实时监控、监控告警
"""

from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import logging
import threading

logger = logging.getLogger(__name__)


class MonitorType(Enum):
    """监控类型"""
    PERFORMANCE = "performance"  # 性能监控
    QUALITY = "quality"  # 质量监控
    ERROR = "error"  # 错误监控
    RESOURCE = "resource"  # 资源监控


class AlertLevel(Enum):
    """告警级别"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class MonitorRule:
    """监控规则"""
    rule_id: str
    monitor_type: MonitorType
    threshold: float
    alert_level: AlertLevel
    enabled: bool = True


@dataclass
class MonitorMetric:
    """监控指标"""
    metric_id: str
    metric_name: str
    value: float
    timestamp: datetime
    metadata: Dict[str, Any] = None


@dataclass
class Alert:
    """告警"""
    alert_id: str
    rule_id: str
    level: AlertLevel
    message: str
    metric_value: float
    threshold: float
    timestamp: datetime


class DataTransformationMonitor:
    """
    数据转换监控器
    
    专注于数据转换监控、实时监控、监控告警
    """
    
    def __init__(self):
        self.rules: Dict[str, MonitorRule] = {}
        self.metrics: List[MonitorMetric] = []
        self.alerts: List[Alert] = []
        self.monitoring_active = False
        self.monitoring_thread: Optional[threading.Thread] = None
    
    def add_rule(self, rule_config: Dict[str, Any]) -> MonitorRule:
        """
        添加监控规则
        
        Args:
            rule_config: 规则配置
            
        Returns:
            监控规则对象
        """
        rule_id = rule_config.get('rule_id', f"rule_{datetime.utcnow().timestamp()}")
        
        rule = MonitorRule(
            rule_id=rule_id,
            monitor_type=MonitorType(rule_config.get('monitor_type', 'performance')),
            threshold=rule_config.get('threshold', 1.0),
            alert_level=AlertLevel(rule_config.get('alert_level', 'warning')),
            enabled=rule_config.get('enabled', True)
        )
        
        self.rules[rule_id] = rule
        return rule
    
    def record_metric(self, metric_name: str, value: float, metadata: Optional[Dict[str, Any]] = None) -> MonitorMetric:
        """
        记录指标
        
        Args:
            metric_name: 指标名称
            value: 指标值
            metadata: 元数据
            
        Returns:
            监控指标对象
        """
        metric_id = f"metric_{datetime.utcnow().timestamp()}"
        
        metric = MonitorMetric(
            metric_id=metric_id,
            metric_name=metric_name,
            value=value,
            timestamp=datetime.utcnow(),
            metadata=metadata or {}
        )
        
        self.metrics.append(metric)
        
        # 检查告警
        self._check_alerts(metric)
        
        return metric
    
    def _check_alerts(self, metric: MonitorMetric):
        """检查告警"""
        for rule in self.rules.values():
            if not rule.enabled:
                continue
            
            # 根据监控类型检查
            if rule.monitor_type == MonitorType.PERFORMANCE:
                if metric.value > rule.threshold:
                    self._trigger_alert(rule, metric.value, metric.metric_name)
            
            elif rule.monitor_type == MonitorType.ERROR:
                if metric.value > rule.threshold:
                    self._trigger_alert(rule, metric.value, metric.metric_name)
        
        # 只保留最近1000条指标
        if len(self.metrics) > 1000:
            self.metrics = self.metrics[-1000:]
    
    def _trigger_alert(self, rule: MonitorRule, value: float, metric_name: str):
        """触发告警"""
        alert = Alert(
            alert_id=f"alert_{datetime.utcnow().timestamp()}",
            rule_id=rule.rule_id,
            level=rule.alert_level,
            message=f"指标 {metric_name} 值 {value:.2f} 超过阈值 {rule.threshold:.2f}",
            metric_value=value,
            threshold=rule.threshold,
            timestamp=datetime.utcnow()
        )
        
        self.alerts.append(alert)
        logger.warning(f"监控告警: {alert.message}")
        
        # 只保留最近100条告警
        if len(self.alerts) > 100:
            self.alerts = self.alerts[-100:]
    
    def get_metrics_summary(self, metric_name: Optional[str] = None,
                           start_time: Optional[datetime] = None,
                           end_time: Optional[datetime] = None) -> Dict[str, Any]:
        """
        获取指标摘要
        
        Args:
            metric_name: 指标名称（可选）
            start_time: 开始时间（可选）
            end_time: 结束时间（可选）
            
        Returns:
            指标摘要
        """
        filtered_metrics = self.metrics
        
        if metric_name:
            filtered_metrics = [m for m in filtered_metrics if m.metric_name == metric_name]
        
        if start_time:
            filtered_metrics = [m for m in filtered_metrics if m.timestamp >= start_time]
        
        if end_time:
            filtered_metrics = [m for m in filtered_metrics if m.timestamp <= end_time]
        
        if not filtered_metrics:
            return {
                'total_metrics': 0,
                'metric_name': metric_name
            }
        
        values = [m.value for m in filtered_metrics]
        
        return {
            'total_metrics': len(filtered_metrics),
            'metric_name': metric_name,
            'min_value': min(values),
            'max_value': max(values),
            'avg_value': sum(values) / len(values),
            'latest_value': filtered_metrics[-1].value if filtered_metrics else None
        }
    
    def get_monitor_summary(self) -> Dict[str, Any]:
        """
        获取监控摘要
        
        Returns:
            监控摘要
        """
        return {
            'total_rules': len(self.rules),
            'enabled_rules': sum(1 for r in self.rules.values() if r.enabled),
            'total_metrics': len(self.metrics),
            'total_alerts': len(self.alerts),
            'recent_alerts': [
                {
                    'alert_id': a.alert_id,
                    'level': a.level.value,
                    'message': a.message,
                    'timestamp': a.timestamp.isoformat()
                }
                for a in self.alerts[-10:]
            ]
        }


def main():
    """主函数 - 示例用法"""
    monitor = DataTransformationMonitor()
    
    # 添加监控规则
    rule = monitor.add_rule({
        'monitor_type': 'performance',
        'threshold': 1.0,
        'alert_level': 'warning'
    })
    
    # 记录指标
    metric = monitor.record_metric('execution_time', 1.5)
    print(f"指标已记录: {metric.metric_name}={metric.value}")


if __name__ == '__main__':
    main()
