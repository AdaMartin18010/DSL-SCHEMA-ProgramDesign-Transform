"""
食品行业Schema转换器

专注于EPCIS事件处理、追溯链查询、质量监控
"""

from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from .logger import logger
from .exceptions import ProcessingError, ValidationError


class EPCISEventType(Enum):
    """EPCIS事件类型"""
    OBJECT_EVENT = "ObjectEvent"
    AGGREGATION_EVENT = "AggregationEvent"
    TRANSACTION_EVENT = "TransactionEvent"
    TRANSFORMATION_EVENT = "TransformationEvent"


class TraceDirection(Enum):
    """追溯方向"""
    FORWARD = "forward"  # 正向追溯（从生产到销售）
    BACKWARD = "backward"  # 反向追溯（从销售到生产）


@dataclass
class EPCISEvent:
    """EPCIS事件"""
    event_id: str
    event_type: EPCISEventType
    epc: Optional[str] = None
    parent_id: Optional[str] = None
    child_epcs: List[str] = None
    input_epcs: List[str] = None
    output_epcs: List[str] = None
    transaction_id: Optional[str] = None
    action: Optional[str] = None
    biz_step: Optional[str] = None
    event_time: datetime = None
    read_point: Optional[str] = None
    biz_location: Optional[str] = None
    event_data: Dict[str, Any] = None


@dataclass
class TraceabilityChain:
    """追溯链"""
    chain_id: str
    epc: str
    events: List[EPCISEvent]
    direction: TraceDirection
    created_at: datetime


@dataclass
class QualityRule:
    """质量规则"""
    rule_id: str
    name: str
    field: str
    rule_type: str  # threshold, range, pattern
    rule_config: Dict[str, Any]
    threshold: float = 0.95


class FoodIndustryConverter:
    """
    食品行业转换器
    
    专注于EPCIS事件处理、追溯链查询、质量监控
    """
    
    def __init__(self):
        self.events: Dict[str, EPCISEvent] = {}
        self.traceability_chains: Dict[str, TraceabilityChain] = {}
        self.quality_rules: Dict[str, QualityRule] = {}
        self.epc_index: Dict[str, List[str]] = {}  # EPC到事件ID的索引
        logger.info("FoodIndustryConverter initialized")
    
    def process_epcis_event(self, event_data: Dict[str, Any]) -> EPCISEvent:
        """
        处理EPCIS事件
        
        Args:
            event_data: 事件数据
            
        Returns:
            EPCIS事件对象
            
        Raises:
            ProcessingError: 处理失败时抛出
            ValidationError: 数据验证失败时抛出
        """
        try:
            # 验证输入
            if not event_data:
                raise ValidationError("事件数据不能为空")
            
            # 验证事件类型
            event_type_str = event_data.get('event_type', 'ObjectEvent')
            try:
                event_type = EPCISEventType(event_type_str)
            except ValueError:
                raise ValidationError(f"无效的事件类型: {event_type_str}")
            
            event_id = event_data.get('event_id', f"event_{datetime.utcnow().timestamp()}")
            logger.debug(f"处理EPCIS事件: {event_id} (类型: {event_type.value})")
            
            # 解析事件时间
            event_time_str = event_data.get('event_time')
            if event_time_str:
                try:
                    if isinstance(event_time_str, str):
                        event_time = datetime.fromisoformat(event_time_str.replace('Z', '+00:00'))
                    else:
                        event_time = event_time_str
                except (ValueError, AttributeError) as e:
                    logger.warning(f"事件时间解析失败，使用当前时间: {str(e)}")
                    event_time = datetime.utcnow()
            else:
                event_time = datetime.utcnow()
            
            event = EPCISEvent(
                event_id=event_id,
                event_type=event_type,
                epc=event_data.get('epc'),
                parent_id=event_data.get('parent_id'),
                child_epcs=event_data.get('child_epcs', []),
                input_epcs=event_data.get('input_epcs', []),
                output_epcs=event_data.get('output_epcs', []),
                transaction_id=event_data.get('transaction_id'),
                action=event_data.get('action'),
                biz_step=event_data.get('biz_step'),
                event_time=event_time,
                read_point=event_data.get('read_point'),
                biz_location=event_data.get('biz_location'),
                event_data=event_data.get('event_data', {})
            )
            
            self.events[event_id] = event
            
            # 更新EPC索引
            if event.epc:
                if event.epc not in self.epc_index:
                    self.epc_index[event.epc] = []
                self.epc_index[event.epc].append(event_id)
            
            # 处理聚合事件
            if event_type == EPCISEventType.AGGREGATION_EVENT:
                if event.parent_id:
                    if event.parent_id not in self.epc_index:
                        self.epc_index[event.parent_id] = []
                    self.epc_index[event.parent_id].append(event_id)
            
            for child_epc in event.child_epcs:
                if child_epc not in self.epc_index:
                    self.epc_index[child_epc] = []
                self.epc_index[child_epc].append(event_id)
            
            # 处理转换事件
            if event_type == EPCISEventType.TRANSFORMATION_EVENT:
                for input_epc in event.input_epcs:
                    if input_epc not in self.epc_index:
                        self.epc_index[input_epc] = []
                    self.epc_index[input_epc].append(event_id)
                
                for output_epc in event.output_epcs:
                    if output_epc not in self.epc_index:
                        self.epc_index[output_epc] = []
                    self.epc_index[output_epc].append(event_id)
            
            logger.info(f"EPCIS事件处理成功: {event_id}")
            return event
            
        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"EPCIS事件处理失败: {str(e)}", exc_info=True)
            raise ProcessingError(f"事件处理失败: {str(e)}") from e
    
    def trace_forward(self, epc: str, max_depth: int = 10) -> TraceabilityChain:
        """
        正向追溯（从生产到销售）
        
        Args:
            epc: EPC代码
            max_depth: 最大深度
            
        Returns:
            追溯链对象
            
        Raises:
            ProcessingError: 追溯失败时抛出
            ValidationError: 输入验证失败时抛出
        """
        try:
            if not epc:
                raise ValidationError("EPC代码不能为空")
            
            if max_depth <= 0:
                raise ValidationError("最大深度必须大于0")
            
            logger.debug(f"开始正向追溯: EPC={epc}, max_depth={max_depth}")
            
            chain_id = f"chain_{epc}_{datetime.utcnow().timestamp()}"
            events = []
            visited = set()
        
        def dfs(current_epc: str, depth: int):
            if depth > max_depth or current_epc in visited:
                return
            
            visited.add(current_epc)
            
            # 获取与当前EPC相关的事件
            event_ids = self.epc_index.get(current_epc, [])
            
            for event_id in event_ids:
                if event_id in self.events:
                    event = self.events[event_id]
                    
                    # 只添加输出事件（向前追溯）
                    if event.event_type == EPCISEventType.TRANSFORMATION_EVENT:
                        if current_epc in event.input_epcs:
                            events.append(event)
                            # 继续追溯输出EPC
                            for output_epc in event.output_epcs:
                                dfs(output_epc, depth + 1)
                    elif event.event_type == EPCISEventType.AGGREGATION_EVENT:
                        if current_epc in event.child_epcs:
                            events.append(event)
                            dfs(event.parent_id, depth + 1)
                    else:
                        events.append(event)
        
        dfs(epc, 0)
        
        # 按时间排序
        events.sort(key=lambda e: e.event_time)
        
        chain = TraceabilityChain(
            chain_id=chain_id,
            epc=epc,
            events=events,
            direction=TraceDirection.FORWARD,
            created_at=datetime.utcnow()
        )
        
        self.traceability_chains[chain_id] = chain
        return chain
    
    def trace_backward(self, epc: str, max_depth: int = 10) -> TraceabilityChain:
        """
        反向追溯（从销售到生产）
        
        Args:
            epc: EPC代码
            max_depth: 最大深度
            
        Returns:
            追溯链对象
        """
        chain_id = f"chain_{epc}_{datetime.utcnow().timestamp()}"
        events = []
        visited = set()
        
        def dfs(current_epc: str, depth: int):
            if depth > max_depth or current_epc in visited:
                return
            
            visited.add(current_epc)
            
            # 获取与当前EPC相关的事件
            event_ids = self.epc_index.get(current_epc, [])
            
            for event_id in event_ids:
                if event_id in self.events:
                    event = self.events[event_id]
                    
                    # 只添加输入事件（向后追溯）
                    if event.event_type == EPCISEventType.TRANSFORMATION_EVENT:
                        if current_epc in event.output_epcs:
                            events.append(event)
                            # 继续追溯输入EPC
                            for input_epc in event.input_epcs:
                                dfs(input_epc, depth + 1)
                    elif event.event_type == EPCISEventType.AGGREGATION_EVENT:
                        if current_epc == event.parent_id:
                            events.append(event)
                            for child_epc in event.child_epcs:
                                dfs(child_epc, depth + 1)
                    else:
                        events.append(event)
        
        dfs(epc, 0)
        
        # 按时间倒序排序
        events.sort(key=lambda e: e.event_time, reverse=True)
        
        chain = TraceabilityChain(
            chain_id=chain_id,
            epc=epc,
            events=events,
            direction=TraceDirection.BACKWARD,
            created_at=datetime.utcnow()
        )
        
        self.traceability_chains[chain_id] = chain
        return chain
    
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
            name=rule_config.get('name', ''),
            field=rule_config.get('field', ''),
            rule_type=rule_config.get('rule_type', 'threshold'),
            rule_config=rule_config.get('rule_config', {}),
            threshold=rule_config.get('threshold', 0.95)
        )
        
        self.quality_rules[rule_id] = rule
        return rule
    
    def check_quality(self, food_data: Dict[str, Any], rule_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        质量检查
        
        Args:
            food_data: 食品数据
            rule_ids: 规则ID列表（可选，默认使用所有规则）
            
        Returns:
            质量检查结果
        """
        rules_to_check = rule_ids if rule_ids else list(self.quality_rules.keys())
        
        passed = 0
        failed = 0
        issues = []
        
        for rule_id in rules_to_check:
            if rule_id not in self.quality_rules:
                continue
            
            rule = self.quality_rules[rule_id]
            field = rule.field
            
            if field not in food_data:
                failed += 1
                issues.append({
                    'rule_id': rule_id,
                    'rule_name': rule.name,
                    'field': field,
                    'issue': f'字段 {field} 不存在'
                })
                continue
            
            value = food_data[field]
            rule_type = rule.rule_type
            
            # 应用规则
            if rule_type == 'threshold':
                threshold = rule.rule_config.get('threshold')
                if isinstance(value, (int, float)) and value < threshold:
                    failed += 1
                    issues.append({
                        'rule_id': rule_id,
                        'rule_name': rule.name,
                        'field': field,
                        'value': value,
                        'threshold': threshold,
                        'issue': f'值 {value} 低于阈值 {threshold}'
                    })
                else:
                    passed += 1
            
            elif rule_type == 'range':
                min_val = rule.rule_config.get('min')
                max_val = rule.rule_config.get('max')
                
                if isinstance(value, (int, float)):
                    if min_val is not None and value < min_val:
                        failed += 1
                        issues.append({
                            'rule_id': rule_id,
                            'rule_name': rule.name,
                            'field': field,
                            'value': value,
                            'min': min_val,
                            'issue': f'值 {value} 小于最小值 {min_val}'
                        })
                    elif max_val is not None and value > max_val:
                        failed += 1
                        issues.append({
                            'rule_id': rule_id,
                            'rule_name': rule.name,
                            'field': field,
                            'value': value,
                            'max': max_val,
                            'issue': f'值 {value} 大于最大值 {max_val}'
                        })
                    else:
                        passed += 1
            
            elif rule_type == 'pattern':
                pattern = rule.rule_config.get('pattern', '')
                import re
                if not re.match(pattern, str(value)):
                    failed += 1
                    issues.append({
                        'rule_id': rule_id,
                        'rule_name': rule.name,
                        'field': field,
                        'value': value,
                        'pattern': pattern,
                        'issue': f'值 {value} 不匹配模式 {pattern}'
                    })
                else:
                    passed += 1
        
        total = passed + failed
        quality_score = (passed / total * 100) if total > 0 else 0.0
        
        return {
            'quality_score': quality_score,
            'passed': passed,
            'failed': failed,
            'total': total,
            'issues': issues
        }


def main():
    """主函数 - 示例用法"""
    converter = FoodIndustryConverter()
    
    # 处理EPCIS事件
    event_data = {
        'event_type': 'ObjectEvent',
        'epc': 'urn:epc:id:sgtin:0614141.107346.20240121',
        'action': 'OBSERVE',
        'biz_step': 'shipping',
        'event_time': datetime.utcnow().isoformat(),
        'read_point': 'Warehouse A',
        'biz_location': 'Distribution Center'
    }
    
    event = converter.process_epcis_event(event_data)
    print(f"EPCIS事件: {event.event_id}")
    
    # 正向追溯
    chain = converter.trace_forward(event.epc)
    print(f"追溯链: {len(chain.events)} 个事件")
    
    # 添加质量规则
    rule = converter.add_quality_rule({
        'name': '温度检查',
        'field': 'temperature',
        'rule_type': 'range',
        'rule_config': {'min': -18, 'max': 4},
        'threshold': 0.95
    })
    
    # 质量检查
    food_data = {
        'temperature': 2.5,
        'humidity': 60
    }
    
    quality_result = converter.check_quality(food_data, [rule.rule_id])
    print(f"质量检查: 分数={quality_result['quality_score']:.1f}%")


if __name__ == '__main__':
    main()
