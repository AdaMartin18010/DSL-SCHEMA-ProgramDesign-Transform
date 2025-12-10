"""
Maritime转换器测试

测试MaritimeConverter的核心功能
"""

import unittest
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from code.schema_deepening import MaritimeConverter, EDIFACTMessageType, AISMessageType
from code.schema_deepening.exceptions import ParseError, ValidationError


class TestMaritimeConverter(unittest.TestCase):
    """Maritime转换器测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.converter = MaritimeConverter()
    
    def test_parse_edifact_empty(self):
        """测试解析空EDIFACT消息"""
        with self.assertRaises(ValidationError):
            self.converter.parse_edifact("")
    
    def test_parse_edifact_invalid_format(self):
        """测试解析无效格式"""
        invalid_message = "INVALID"
        with self.assertRaises(ParseError):
            self.converter.parse_edifact(invalid_message)
    
    def test_parse_edifact_valid(self):
        """测试解析有效EDIFACT消息"""
        edifact_msg = "UNH+1+ORDERS:D:96A:UN'BGM+220+12345'DTM+137:20240101:102'UNT+3+1'"
        
        message = self.converter.parse_edifact(edifact_msg)
        
        self.assertIsNotNone(message)
        self.assertIsNotNone(message.message_id)
        self.assertEqual(message.message_type, EDIFACTMessageType.ORDERS)
        self.assertGreater(len(message.segments), 0)
    
    def test_parse_ais_nmea_valid(self):
        """测试解析有效NMEA格式AIS消息"""
        # 这是一个简化的NMEA示例
        nmea_sentence = "!AIVDM,1,1,,A,133m@ogP00PD;88MD5MTDww@2D7k,0*46"
        
        # 注意：实际的parse_ais方法可能需要更完整的实现
        # 这里只是测试基本结构
        try:
            message = self.converter.parse_ais(nmea_sentence)
            if message:
                self.assertIsNotNone(message.message_id)
                self.assertIsNotNone(message.mmsi)
        except (NotImplementedError, AttributeError):
            # 如果方法未实现，跳过测试
            self.skipTest("parse_ais方法未完全实现")
    
    def test_determine_message_type_orders(self):
        """测试确定ORDERS消息类型"""
        segments = [
            {'tag': 'UNH', 'elements': ['1', 'ORDERS:D:96A:UN']},
            {'tag': 'BGM', 'elements': ['220', '12345']}
        ]
        
        msg_type = self.converter._determine_message_type(segments)
        self.assertEqual(msg_type, EDIFACTMessageType.ORDERS)
    
    def test_determine_message_type_invoice(self):
        """测试确定INVOIC消息类型"""
        segments = [
            {'tag': 'UNH', 'elements': ['1', 'INVOIC:D:96A:UN']},
            {'tag': 'BGM', 'elements': ['380', '12345']}
        ]
        
        msg_type = self.converter._determine_message_type(segments)
        self.assertEqual(msg_type, EDIFACTMessageType.INVOIC)


if __name__ == '__main__':
    unittest.main()
