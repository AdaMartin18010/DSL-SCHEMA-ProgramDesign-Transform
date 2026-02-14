"""
智慧家居存储测试

测试SmartHomeStorage的核心功能
"""

import unittest
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from unittest.mock import Mock, patch, MagicMock
from schema_deepening import SmartHomeStorage
from schema_deepening.exceptions import StorageError, ValidationError


class TestSmartHomeStorage(unittest.TestCase):
    """智慧家居存储测试类"""
    
    @patch('code.schema_deepening.smart_home_storage.psycopg2')
    def setUp(self, mock_psycopg2):
        """测试前准备"""
        # 模拟数据库连接
        self.mock_conn = MagicMock()
        self.mock_cur = MagicMock()
        self.mock_conn.cursor.return_value = self.mock_cur
        mock_psycopg2.connect.return_value = self.mock_conn
        
        self.storage = SmartHomeStorage("postgresql://localhost/test_db")
    
    def test_store_device(self):
        """测试存储设备"""
        device = {
            'device_id': 'device_1',
            'name': '测试设备',
            'device_type': 'light',
            'protocol': 'matter',
            'state': {'power': True},
            'capabilities': ['on_off']
        }
        
        result = self.storage.store_device(device)
        
        self.assertTrue(result)
        self.mock_cur.execute.assert_called()
        self.mock_conn.commit.assert_called()
    
    def test_store_device_empty(self):
        """测试存储空设备"""
        with self.assertRaises(ValidationError):
            self.storage.store_device({})
    
    def test_store_device_missing_id(self):
        """测试存储缺少ID的设备"""
        device = {
            'name': '测试设备'
        }
        
        with self.assertRaises(ValidationError):
            self.storage.store_device(device)
    
    def test_store_scene(self):
        """测试存储场景"""
        scene = {
            'scene_id': 'scene_1',
            'name': '测试场景',
            'triggers': [{'type': 'manual'}],
            'actions': [{'type': 'set_state'}]
        }
        
        result = self.storage.store_scene(scene)
        
        self.assertTrue(result)
        self.mock_cur.execute.assert_called()
        self.mock_conn.commit.assert_called()
    
    def test_store_scene_empty(self):
        """测试存储空场景"""
        with self.assertRaises(ValidationError):
            self.storage.store_scene({})
    
    def test_query_device_state_history(self):
        """测试查询设备状态历史"""
        # 模拟查询结果
        self.mock_cur.fetchall.return_value = [
            ('{"power": true}', '2024-01-01 10:00:00'),
            ('{"power": false}', '2024-01-01 09:00:00')
        ]
        
        results = self.storage.query_device_state_history('device_1')
        
        self.assertEqual(len(results), 2)
        self.assertIn('state', results[0])
        self.assertIn('changed_at', results[0])
        self.mock_cur.execute.assert_called()
    
    def test_query_device_state_history_empty_id(self):
        """测试查询时设备ID为空"""
        with self.assertRaises(ValidationError):
            self.storage.query_device_state_history('')
    
    @patch('code.schema_deepening.smart_home_storage.psycopg2')
    def test_storage_connection_error(self, mock_psycopg2):
        """测试数据库连接错误"""
        mock_psycopg2.connect.side_effect = Exception("Connection failed")
        
        with self.assertRaises(StorageError):
            SmartHomeStorage("postgresql://localhost/test_db")


if __name__ == '__main__':
    unittest.main()
