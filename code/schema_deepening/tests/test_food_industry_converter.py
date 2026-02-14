"""
Food Industry转换器测试

测试FoodIndustryConverter的核心功能
"""

import unittest
import sys
from pathlib import Path
from datetime import datetime

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from schema_deepening import FoodIndustryConverter, EPCISEventType, TraceDirection
from schema_deepening.exceptions import ProcessingError, ValidationError


class TestFoodIndustryConverter(unittest.TestCase):
    """Food Industry转换器测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.converter = FoodIndustryConverter()
    
    def test_process_epcis_event_empty(self):
        """测试处理空事件"""
        with self.assertRaises(ValidationError):
            self.converter.process_epcis_event({})
    
    def test_process_epcis_event_invalid_type(self):
        """测试无效事件类型"""
        event_data = {
            'event_type': 'InvalidEventType',
            'epc': 'urn:epc:id:sgtin:0614141.107346.2017'
        }
        
        with self.assertRaises(ValidationError):
            self.converter.process_epcis_event(event_data)
    
    def test_process_epcis_event_object_event(self):
        """测试处理ObjectEvent"""
        event_data = {
            'event_type': 'ObjectEvent',
            'epc': 'urn:epc:id:sgtin:0614141.107346.2017',
            'action': 'OBSERVE',
            'biz_step': 'receiving',
            'event_time': datetime.utcnow().isoformat(),
            'read_point': 'urn:epc:id:sgln:0614141.00725.0',
            'biz_location': 'urn:epc:id:sgln:0614141.00725.0'
        }
        
        event = self.converter.process_epcis_event(event_data)
        
        self.assertIsNotNone(event)
        self.assertEqual(event.event_type, EPCISEventType.OBJECT_EVENT)
        self.assertEqual(event.epc, event_data['epc'])
        self.assertIn(event.event_id, self.converter.events)
    
    def test_process_epcis_event_aggregation_event(self):
        """测试处理AggregationEvent"""
        event_data = {
            'event_type': 'AggregationEvent',
            'parent_id': 'urn:epc:id:sgtin:0614141.107346.2017',
            'child_epcs': ['urn:epc:id:sgtin:0614141.107347.2017'],
            'action': 'ADD',
            'biz_step': 'packing',
            'event_time': datetime.utcnow().isoformat()
        }
        
        event = self.converter.process_epcis_event(event_data)
        
        self.assertIsNotNone(event)
        self.assertEqual(event.event_type, EPCISEventType.AGGREGATION_EVENT)
        self.assertEqual(event.parent_id, event_data['parent_id'])
        self.assertEqual(len(event.child_epcs), 1)
    
    def test_trace_forward_empty_epc(self):
        """测试正向追溯空EPC"""
        with self.assertRaises(ValidationError):
            self.converter.trace_forward("")
    
    def test_trace_forward_invalid_depth(self):
        """测试无效深度"""
        with self.assertRaises(ValidationError):
            self.converter.trace_forward("epc", max_depth=0)
    
    def test_trace_backward_empty_epc(self):
        """测试反向追溯空EPC"""
        with self.assertRaises(ValidationError):
            self.converter.trace_backward("")
    
    def test_check_quality_empty_data(self):
        """测试质量检查空数据"""
        with self.assertRaises(ValidationError):
            self.converter.check_quality({})
    
    def test_register_quality_rule(self):
        """测试注册质量规则"""
        rule_config = {
            'rule_id': 'rule_1',
            'name': '温度检查',
            'field': 'temperature',
            'rule_type': 'range',
            'rule_config': {'min': -20, 'max': 5},
            'threshold': 0.95
        }
        
        rule = self.converter.register_quality_rule(rule_config)
        
        self.assertIsNotNone(rule)
        self.assertEqual(rule.rule_id, 'rule_1')
        self.assertEqual(rule.name, '温度检查')
        self.assertIn('rule_1', self.converter.quality_rules)


if __name__ == '__main__':
    unittest.main()
