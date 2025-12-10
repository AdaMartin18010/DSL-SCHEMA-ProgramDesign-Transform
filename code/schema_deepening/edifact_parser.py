"""
EDIFACT解析器

专注于EDIFACT消息解析、验证、转换
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import re

from .logger import logger
from .exceptions import ParseError, ValidationError


class EDIFACTMessageType(Enum):
    """EDIFACT消息类型"""
    ORDERS = "ORDERS"  # 订单
    ORDRSP = "ORDRSP"  # 订单响应
    DESADV = "DESADV"  # 发货通知
    INVOIC = "INVOIC"  # 发票
    IFTMIN = "IFTMIN"  # 运输指令
    IFTMCS = "IFTMCS"  # 运输状态
    COMDIS = "COMDIS"  # 商业争议
    CONTRL = "CONTRL"  # 控制消息


@dataclass
class EDIFACTSegment:
    """EDIFACT段"""
    tag: str
    name: str
    elements: List[List[str]]  # 元素列表（支持复合元素）


@dataclass
class EDIFACTMessage:
    """EDIFACT消息"""
    message_id: str
    message_type: EDIFACTMessageType
    segments: List[EDIFACTSegment]
    created_at: datetime


class EDIFACTParser:
    """
    EDIFACT解析器
    
    专注于EDIFACT消息解析、验证、转换
    """
    
    def __init__(self):
        self.segment_definitions: Dict[str, Dict[str, Any]] = {}
        self.message_types: Dict[str, EDIFACTMessageType] = {}
        self._init_segment_definitions()
        logger.info("EDIFACTParser initialized")
        self._init_message_types()
    
    def _init_segment_definitions(self):
        """初始化段定义"""
        self.segment_definitions = {
            'UNH': {
                'name': 'Message Header',
                'elements': ['Message Reference Number', 'Message Type', 'Message Version', 'Message Release Number', 'Controlling Agency', 'Association Assigned Code']
            },
            'BGM': {
                'name': 'Beginning of Message',
                'elements': ['Document Message Name', 'Document Message Number', 'Message Function Code', 'Response Type Code']
            },
            'DTM': {
                'name': 'Date/Time/Period',
                'elements': ['Date/Time/Period Qualifier', 'Date/Time/Period', 'Date/Time/Period Format Qualifier']
            },
            'NAD': {
                'name': 'Name and Address',
                'elements': ['Party Qualifier', 'Party Identification Details', 'Name and Address', 'City Name', 'Country Sub-entity Details', 'Postal Identification Code', 'Country Coded']
            },
            'LIN': {
                'name': 'Line Item',
                'elements': ['Line Item Number', 'Action Request/Notification Coded', 'Item Number Identification', 'Sub-line Information', 'Configuration Level', 'Configuration Coded']
            },
            'QTY': {
                'name': 'Quantity',
                'elements': ['Quantity Qualifier', 'Quantity', 'Measure Unit Qualifier']
            },
            'PRI': {
                'name': 'Price Details',
                'elements': ['Price Qualifier', 'Price', 'Price Type Qualifier', 'Price Type', 'Price Type Qualifier', 'Price Type', 'Unit Price Basis', 'Measure Unit Qualifier']
            },
            'UNT': {
                'name': 'Message Trailer',
                'elements': ['Number of Segments', 'Message Reference Number']
            }
        }
    
    def _init_message_types(self):
        """初始化消息类型"""
        self.message_types = {
            'ORDERS': EDIFACTMessageType.ORDERS,
            'ORDRSP': EDIFACTMessageType.ORDRSP,
            'DESADV': EDIFACTMessageType.DESADV,
            'INVOIC': EDIFACTMessageType.INVOIC,
            'IFTMIN': EDIFACTMessageType.IFTMIN,
            'IFTMCS': EDIFACTMessageType.IFTMCS,
            'COMDIS': EDIFACTMessageType.COMDIS,
            'CONTRL': EDIFACTMessageType.CONTRL
        }
    
    def parse_message(self, edifact_message: str) -> EDIFACTMessage:
        """
        解析EDIFACT消息
        
        Args:
            edifact_message: EDIFACT消息字符串
            
        Returns:
            EDIFACT消息对象
        """
        # 检测分隔符
        separators = self._detect_separators(edifact_message)
        
        segment_terminator = separators['segment_terminator']
        element_separator = separators['element_separator']
        component_separator = separators['component_separator']
        
        # 解析段
        segments = []
        segment_strings = edifact_message.split(segment_terminator)
        
        for segment_str in segment_strings:
            segment_str = segment_str.strip()
            if not segment_str:
                continue
            
            segment = self._parse_segment(
                segment_str,
                element_separator,
                component_separator
            )
            
            if segment:
                segments.append(segment)
        
        # 确定消息类型
        message_type = self._determine_message_type(segments)
        
        # 创建消息对象
        message_id = f"msg_{datetime.utcnow().timestamp()}"
        message = EDIFACTMessage(
            message_id=message_id,
            message_type=message_type,
            segments=segments,
            created_at=datetime.utcnow()
        )
        
        return message
    
    def _detect_separators(self, message: str) -> Dict[str, str]:
        """检测分隔符"""
        # 默认分隔符
        separators = {
            'segment_terminator': "'",
            'element_separator': "+",
            'component_separator': ":",
            'release_character': "?"
        }
        
        # 尝试从UNA段检测（如果存在）
        if message.startswith('UNA'):
            una_segment = message[:9]  # UNA段通常是9个字符
            if len(una_segment) >= 9:
                separators['component_separator'] = una_segment[3]
                separators['element_separator'] = una_segment[4]
                separators['decimal_mark'] = una_segment[5]
                separators['release_character'] = una_segment[6]
                separators['reserved'] = una_segment[7]
                separators['segment_terminator'] = una_segment[8]
        
        return separators
    
    def _parse_segment(self, segment_str: str, element_separator: str,
                      component_separator: str) -> Optional[EDIFACTSegment]:
        """解析段"""
        if not segment_str:
            return None
        
        # 获取段标识符（前3个字符）
        segment_tag = segment_str[:3]
        
        # 解析元素
        elements = []
        element_strings = segment_str[3:].split(element_separator)
        
        for element_str in element_strings:
            if component_separator in element_str:
                # 复合元素
                components = element_str.split(component_separator)
                elements.append(components)
            else:
                # 简单元素
                elements.append([element_str] if element_str else [])
        
        segment_def = self.segment_definitions.get(segment_tag, {})
        
        return EDIFACTSegment(
            tag=segment_tag,
            name=segment_def.get('name', ''),
            elements=elements
        )
    
    def _determine_message_type(self, segments: List[EDIFACTSegment]) -> EDIFACTMessageType:
        """确定消息类型"""
        for segment in segments:
            if segment.tag == 'UNH':
                # 从UNH段获取消息类型
                if segment.elements and len(segment.elements) > 1:
                    message_type_code = segment.elements[1][0] if segment.elements[1] else ''
                    
                    return self.message_types.get(message_type_code, EDIFACTMessageType.ORDERS)
        
        return EDIFACTMessageType.ORDERS
    
    def validate_message(self, message: EDIFACTMessage) -> Dict[str, Any]:
        """
        验证消息
        
        Args:
            message: EDIFACT消息对象
            
        Returns:
            验证结果
        """
        errors = []
        warnings = []
        
        # 检查UNH段
        unh_segment = next((s for s in message.segments if s.tag == 'UNH'), None)
        if not unh_segment:
            errors.append("消息缺少UNH段（消息头）")
        
        # 检查UNT段
        unt_segment = next((s for s in message.segments if s.tag == 'UNT'), None)
        if not unt_segment:
            errors.append("消息缺少UNT段（消息尾）")
        
        # 验证段计数
        if unh_segment and unt_segment:
            expected_count = len(message.segments)
            actual_count_elem = unt_segment.elements[0] if unt_segment.elements else None
            actual_count = int(actual_count_elem[0]) if actual_count_elem and actual_count_elem[0].isdigit() else 0
            
            if actual_count != expected_count:
                warnings.append(f"段计数不匹配：期望 {expected_count}，实际 {actual_count}")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    def convert_to_xml(self, message: EDIFACTMessage) -> str:
        """
        转换为XML
        
        Args:
            message: EDIFACT消息对象
            
        Returns:
            XML字符串
        """
        from xml.etree.ElementTree import Element, SubElement, tostring
        
        root = Element('EDIFACTMessage')
        root.set('messageId', message.message_id)
        root.set('messageType', message.message_type.value)
        
        for segment in message.segments:
            segment_elem = SubElement(root, 'Segment')
            segment_elem.set('tag', segment.tag)
            segment_elem.set('name', segment.name)
            
            for i, element in enumerate(segment.elements):
                element_elem = SubElement(segment_elem, 'Element')
                element_elem.set('position', str(i + 1))
                
                if len(element) == 1:
                    element_elem.text = element[0]
                else:
                    # 复合元素
                    for j, component in enumerate(element):
                        component_elem = SubElement(element_elem, 'Component')
                        component_elem.set('position', str(j + 1))
                        component_elem.text = component
        
        return tostring(root, encoding='utf-8').decode('utf-8')


def main():
    """主函数 - 示例用法"""
    parser = EDIFACTParser()
    
    # 解析EDIFACT消息
    edifact_msg = "UNH+1+ORDERS:D:96A:UN'BGM+220+12345+9'DTM+2:20250121:102'UNT+3+1'"
    
    message = parser.parse_message(edifact_msg)
    print(f"消息类型: {message.message_type.value}")
    print(f"段数: {len(message.segments)}")
    
    # 验证消息
    validation = parser.validate_message(message)
    print(f"验证结果: {'有效' if validation['valid'] else '无效'}")
    
    # 转换为XML
    xml = parser.convert_to_xml(message)
    print(f"XML: {xml[:100]}...")


if __name__ == '__main__':
    main()
