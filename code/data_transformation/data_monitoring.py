"""
数据监控模块

专注于数据监控、性能监控、告警
"""

from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import logging
import threading
import time

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """指标类型"""
    COUNTER = "counter"  # 计数器
    GAUGE = "gauge"  # 仪表盘
    HISTOGRAM = "histogram"  # 直方图
    SUMMARY = "summary"  # 摘要


class AlertLevel(Enum):
    """告警级别"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class Metric:
    """指标"""
    metric_id: str
    name: str
    metric_type: MetricType
    value: float
    labels: Dict[str, str] = None
    timestamp: datetime = None


@dataclass
class Alert:
    """告警"""
    alert_id: str
    metric_name: str
    level: AlertLevel
    message: str
    threshold: float
    current_value: float
    triggered_at: datetime = None


class DataMonitoring:
    """
    数据监控器
    
    专注于数据监控、性能监控、告警
    """
    
    def __init__(self):
        self.metrics: Dict[str, List[Metric]] = {}
        self.alerts: Dict[str, Alert] = {}
        self.alert_rules: Dict[str, Dict[str, Any]] = {}
        self.monitoring_active = False
        self.monitoring_thread: Optional[threading.Thread] = None
    
    def record_metric(self, name: str, value: float, metric_type: MetricType = MetricType.GAUGE,
                     labels: Optional[Dict[str, str]] = None) -> Metric:
        """
        记录指标
        
        Args:
            name: 指标名称
            value: 指标值
            metric_type: 指标类型
            labels: 标签
            
        Returns:
            指标对象
        """
        metric_id = f"metric_{datetime.utcnow().timestamp()}"
        
        metric = Metric(
            metric_id=metric_id,
            name=name,
            metric_type=metric_type,
            value=value,
            labels=labels or {},
            timestamp=datetime.utcnow()
        )
        
        if name not in self.metrics:
            self.metrics[name] = []
        
        self.metrics[name].append(metric)
        
        # 检查告警规则
        self._check_alerts(name, value)
        
        return metric
    
    def add_alert_rule(self, rule_config: Dict[str, Any]) -> str:
        """
        添加告警规则
        
        Args:
            rule_config: 规则配置
            
        Returns:
            规则ID
        """
        rule_id = rule_config.get('rule_id', f"rule_{datetime.utcnow().timestamp()}")
        
        self.alert_rules[rule_id] = {
            'metric_name': rule_config['metric_name'],
            'threshold': rule_config['threshold'],
            'operator': rule_config.get('operator', '>'),  # >, <, >=, <=, ==
            'level': AlertLevel(rule_config.get('level', 'warning')),
            'message': rule_config.get('message', ''),
            'enabled': rule_config.get('enabled', True)
        }
        
        return rule_id
    
    def _check_alerts(self, metric_name: str, value: float):
        """检查告警"""
        for rule_id, rule in self.alert_rules.items():
            if not rule.get('enabled', True):
                continue
            
            if rule['metric_name'] != metric_name:
                continue
            
            threshold = rule['threshold']
            operator = rule['operator']
            
            # 检查条件
            should_alert = False
            
            if operator == '>' and value > threshold:
                should_alert = True
            elif operator == '<' and value < threshold:
                should_alert = True
            elif operator == '>=' and value >= threshold:
                should_alert = True
            elif operator == '<=' and value <= threshold:
                should_alert = True
            elif operator == '==' and value == threshold:
                should_alert = True
            
            if should_alert:
                self._trigger_alert(rule_id, rule, value)
    
    def _trigger_alert(self, rule_id: str, rule: Dict[str, Any], value: float):
        """触发告警"""
        alert_id = f"alert_{datetime.utcnow().timestamp()}"
        
        alert = Alert(
            alert_id=alert_id,
            metric_name=rule['metric_name'],
            level=rule['level'],
            message=rule.get('message', f"指标 {rule['metric_name']} 超过阈值"),
            threshold=rule['threshold'],
            current_value=value,
            triggered_at=datetime.utcnow()
        )
        
        self.alerts[alert_id] = alert
        
        logger.warning(f"告警触发: {alert.message}, 当前值: {value}, 阈值: {rule['threshold']}")
    
    def get_metric_history(self, metric_name: str, start_time: Optional[datetime] = None,
                          end_time: Optional[datetime] = None) -> List[Metric]:
        """
        获取指标历史
        
        Args:
            metric_name: 指标名称
            start_time: 开始时间
            end_time: 结束时间
            
        Returns:
            指标列表
        """
        if metric_name not in self.metrics:
            return []
        
        metrics = self.metrics[metric_name]
        
        if start_time:
            metrics = [m for m in metrics if m.timestamp >= start_time]
        
        if end_time:
            metrics = [m for m in metrics if m.timestamp <= end_time]
        
        return sorted(metrics, key=lambda m: m.timestamp)
    
    def get_metric_summary(self, metric_name: str, window_minutes: int = 60) -> Dict[str, Any]:
        """
        获取指标摘要
        
        Args:
            metric_name: 指标名称
            window_minutes: 时间窗口（分钟）
            
        Returns:
            指标摘要
        """
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(minutes=window_minutes)
        
        metrics = self.get_metric_history(metric_name, start_time, end_time)
        
        if not metrics:
            return {
                'metric_name': metric_name,
                'count': 0,
                'min': None,
                'max': None,
                'avg': None
            }
        
        values = [m.value for m in metrics]
        
        return {
            'metric_name': metric_name,
            'count': len(values),
            'min': min(values),
            'max': max(values),
            'avg': sum(values) / len(values)
        }
    
    def get_active_alerts(self, level: Optional[AlertLevel] = None) -> List[Alert]:
        """
        获取活跃告警
        
        Args:
            level: 告警级别（可选）
            
        Returns:
            告警列表
        """
        alerts = list(self.alerts.values())
        
        if level:
            alerts = [a for a in alerts if a.level == level]
        
        # 按触发时间排序
        alerts.sort(key=lambda a: a.triggered_at, reverse=True)
        
        return alerts
    
    def clear_alerts(self, alert_ids: Optional[List[str]] = None):
        """
        清除告警
        
        Args:
            alert_ids: 告警ID列表（可选，默认清除所有）
        """
        if alert_ids:
            for alert_id in alert_ids:
                if alert_id in self.alerts:
                    del self.alerts[alert_id]
        else:
            self.alerts.clear()


def main():
    """主函数 - 示例用法"""
    monitoring = DataMonitoring()
    
    # 添加告警规则
    rule_id = monitoring.add_alert_rule({
        'metric_name': 'cpu_usage',
        'threshold': 80.0,
        'operator': '>',
        'level': 'warning',
        'message': 'CPU使用率过高'
    })
    
    # 记录指标
    monitoring.record_metric('cpu_usage', 85.0)
    
    # 获取活跃告警
    alerts = monitoring.get_active_alerts()
    print(f"活跃告警数: {len(alerts)}")


if __name__ == '__main__':
    main()
