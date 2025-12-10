"""
智慧家居转换器测试

测试SmartHomeConverter的核心功能
"""

import unittest
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from unittest.mock import Mock, patch
from code.schema_deepening import (
    SmartHomeConverter,
    DeviceProtocol,
    DeviceType
)
from code.schema_deepening.exceptions import (
    ConversionError,
    DeviceNotFoundError,
    SceneNotFoundError,
    ValidationError
)


class TestSmartHomeConverter(unittest.TestCase):
    """智慧家居转换器测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.converter = SmartHomeConverter()
    
    def test_convert_matter_to_zigbee(self):
        """测试Matter到Zigbee转换"""
        matter_device = {
            'device_id': 'matter_light_1',
            'name': '客厅灯',
            'device_type': 'light',
            'protocol': 'matter',
            'clusters': [{
                'cluster_id': 0x0006,
                'cluster_name': 'OnOff',
                'attributes': {'OnOff': True}
            }]
        }
        
        result = self.converter.convert_matter_to_zigbee(matter_device)
        
        self.assertEqual(result['ieee_address'], 'matter_light_1')
        self.assertEqual(result['friendly_name'], '客厅灯')
        self.assertIn('clusters', result)
        self.assertEqual(len(result['clusters']), 1)
        self.assertEqual(result['clusters'][0]['cluster'], 'OnOff')
    
    def test_convert_matter_to_zigbee_empty_input(self):
        """测试空输入"""
        with self.assertRaises(ValidationError):
            self.converter.convert_matter_to_zigbee({})
    
    def test_convert_matter_to_zigbee_missing_device_id(self):
        """测试缺少设备ID"""
        matter_device = {
            'name': '客厅灯',
            'clusters': []
        }
        
        with self.assertRaises(ValidationError):
            self.converter.convert_matter_to_zigbee(matter_device)
    
    def test_convert_zigbee_to_matter(self):
        """测试Zigbee到Matter转换"""
        zigbee_device = {
            'ieee_address': 'zigbee_light_1',
            'friendly_name': '卧室灯',
            'type': 'light',
            'clusters': [{
                'cluster': 'OnOff',
                'attributes': {'OnOff': False}
            }]
        }
        
        result = self.converter.convert_zigbee_to_matter(zigbee_device)
        
        self.assertEqual(result['device_id'], 'zigbee_light_1')
        self.assertEqual(result['name'], '卧室灯')
        self.assertIn('clusters', result)
        self.assertEqual(len(result['clusters']), 1)
        self.assertEqual(result['clusters'][0]['cluster_name'], 'OnOff')
    
    def test_register_device(self):
        """测试设备注册"""
        device_config = {
            'device_id': 'test_device_1',
            'name': '测试设备',
            'device_type': 'light',
            'protocol': 'matter',
            'state': {'power': True},
            'capabilities': ['on_off']
        }
        
        device = self.converter.register_device(device_config)
        
        self.assertEqual(device.device_id, 'test_device_1')
        self.assertEqual(device.name, '测试设备')
        self.assertEqual(device.device_type, DeviceType.LIGHT)
        self.assertEqual(device.protocol, DeviceProtocol.MATTER)
        self.assertIn('test_device_1', self.converter.devices)
    
    def test_register_device_invalid_type(self):
        """测试无效设备类型"""
        device_config = {
            'device_id': 'test_device_1',
            'device_type': 'invalid_type',
            'protocol': 'matter'
        }
        
        with self.assertRaises(ValidationError):
            self.converter.register_device(device_config)
    
    def test_register_device_invalid_protocol(self):
        """测试无效协议"""
        device_config = {
            'device_id': 'test_device_1',
            'device_type': 'light',
            'protocol': 'invalid_protocol'
        }
        
        with self.assertRaises(ValidationError):
            self.converter.register_device(device_config)
    
    def test_create_scene(self):
        """测试创建场景"""
        scene_config = {
            'name': '回家场景',
            'triggers': [{'type': 'manual'}],
            'actions': [{
                'type': 'set_state',
                'device_id': 'device_1',
                'attribute': 'power',
                'value': True
            }]
        }
        
        scene = self.converter.create_scene(scene_config)
        
        self.assertIsNotNone(scene.scene_id)
        self.assertEqual(scene.name, '回家场景')
        self.assertEqual(len(scene.triggers), 1)
        self.assertEqual(len(scene.actions), 1)
        self.assertIn(scene.scene_id, self.converter.scenes)
    
    def test_execute_scene_not_found(self):
        """测试执行不存在的场景"""
        with self.assertRaises(SceneNotFoundError):
            self.converter.execute_scene('non_existent_scene')
    
    def test_execute_scene_device_not_found(self):
        """测试执行场景时设备不存在"""
        # 创建场景
        scene_config = {
            'name': '测试场景',
            'actions': [{
                'type': 'set_state',
                'device_id': 'non_existent_device',
                'attribute': 'power',
                'value': True
            }]
        }
        scene = self.converter.create_scene(scene_config)
        
        # 执行场景应该抛出异常
        with self.assertRaises(DeviceNotFoundError):
            self.converter.execute_scene(scene.scene_id)
    
    def test_execute_scene_success(self):
        """测试成功执行场景"""
        # 注册设备
        device = self.converter.register_device({
            'device_id': 'test_device_1',
            'name': '测试设备',
            'device_type': 'light',
            'protocol': 'matter',
            'state': {'power': False}
        })
        
        # 创建场景
        scene_config = {
            'name': '测试场景',
            'actions': [{
                'type': 'set_state',
                'device_id': 'test_device_1',
                'attribute': 'power',
                'value': True
            }]
        }
        scene = self.converter.create_scene(scene_config)
        
        # 执行场景
        result = self.converter.execute_scene(scene.scene_id)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['scene_id'], scene.scene_id)
        self.assertEqual(len(result['results']), 1)
        self.assertTrue(result['results'][0]['success'])
        self.assertTrue(device.state['power'])
    
    def test_execute_scene_disabled(self):
        """测试执行已禁用的场景"""
        scene_config = {
            'name': '禁用场景',
            'enabled': False,
            'actions': []
        }
        scene = self.converter.create_scene(scene_config)
        
        result = self.converter.execute_scene(scene.scene_id)
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)
    
    def test_execute_action_toggle(self):
        """测试切换动作"""
        device = self.converter.register_device({
            'device_id': 'test_device_1',
            'name': '测试设备',
            'device_type': 'light',
            'protocol': 'matter',
            'state': {'power': False}
        })
        
        action = {
            'type': 'toggle',
            'device_id': 'test_device_1',
            'attribute': 'power'
        }
        
        result = self.converter._execute_action(action, None)
        
        self.assertTrue(result['success'])
        self.assertTrue(device.state['power'])
        
        # 再次切换
        result = self.converter._execute_action(action, None)
        self.assertFalse(device.state['power'])


if __name__ == '__main__':
    unittest.main()
