"""
数据序列化模块

专注于数据序列化、反序列化、格式转换
"""

from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import json
import pickle
import yaml
import csv
import xml.etree.ElementTree as ET
import logging

logger = logging.getLogger(__name__)


class SerializationFormat(Enum):
    """序列化格式"""
    JSON = "json"
    XML = "xml"
    YAML = "yaml"
    CSV = "csv"
    PICKLE = "pickle"
    PROTOBUF = "protobuf"
    AVRO = "avro"
    MESSAGE_PACK = "messagepack"


class DataSerialization:
    """
    数据序列化器
    
    专注于数据序列化、反序列化、格式转换
    """
    
    def __init__(self):
        self.serialization_history: List[Dict[str, Any]] = []
    
    def serialize(self, data: Any, format_type: SerializationFormat,
                 **kwargs) -> Union[str, bytes]:
        """
        序列化数据
        
        Args:
            data: 要序列化的数据
            format_type: 序列化格式
            **kwargs: 额外参数
            
        Returns:
            序列化后的数据
        """
        try:
            if format_type == SerializationFormat.JSON:
                return json.dumps(data, ensure_ascii=False, indent=kwargs.get('indent', 2))
            
            elif format_type == SerializationFormat.XML:
                return self._serialize_to_xml(data)
            
            elif format_type == SerializationFormat.YAML:
                return yaml.dump(data, default_flow_style=False, allow_unicode=True)
            
            elif format_type == SerializationFormat.CSV:
                return self._serialize_to_csv(data, **kwargs)
            
            elif format_type == SerializationFormat.PICKLE:
                return pickle.dumps(data)
            
            else:
                raise ValueError(f"不支持的序列化格式: {format_type}")
        
        except Exception as e:
            logger.error(f"序列化失败: {e}")
            raise
    
    def deserialize(self, serialized_data: Union[str, bytes],
                   format_type: SerializationFormat) -> Any:
        """
        反序列化数据
        
        Args:
            serialized_data: 序列化的数据
            format_type: 序列化格式
            
        Returns:
            反序列化后的数据
        """
        try:
            if format_type == SerializationFormat.JSON:
                if isinstance(serialized_data, bytes):
                    serialized_data = serialized_data.decode('utf-8')
                return json.loads(serialized_data)
            
            elif format_type == SerializationFormat.XML:
                if isinstance(serialized_data, bytes):
                    serialized_data = serialized_data.decode('utf-8')
                return self._deserialize_from_xml(serialized_data)
            
            elif format_type == SerializationFormat.YAML:
                if isinstance(serialized_data, bytes):
                    serialized_data = serialized_data.decode('utf-8')
                return yaml.safe_load(serialized_data)
            
            elif format_type == SerializationFormat.CSV:
                if isinstance(serialized_data, bytes):
                    serialized_data = serialized_data.decode('utf-8')
                return self._deserialize_from_csv(serialized_data)
            
            elif format_type == SerializationFormat.PICKLE:
                if isinstance(serialized_data, str):
                    serialized_data = serialized_data.encode('latin-1')
                return pickle.loads(serialized_data)
            
            else:
                raise ValueError(f"不支持的反序列化格式: {format_type}")
        
        except Exception as e:
            logger.error(f"反序列化失败: {e}")
            raise
    
    def convert_format(self, data: Any, source_format: SerializationFormat,
                      target_format: SerializationFormat) -> Union[str, bytes]:
        """
        转换数据格式
        
        Args:
            data: 数据
            source_format: 源格式
            target_format: 目标格式
            
        Returns:
            转换后的数据
        """
        # 先反序列化，再序列化
        if source_format == target_format:
            return self.serialize(data, source_format)
        
        # 如果是对象，先转换为字典
        if hasattr(data, '__dict__'):
            data = asdict(data) if isinstance(data, type) else data.__dict__
        
        # 序列化到目标格式
        return self.serialize(data, target_format)
    
    def _serialize_to_xml(self, data: Any, root_name: str = 'root') -> str:
        """序列化为XML"""
        root = ET.Element(root_name)
        
        if isinstance(data, dict):
            for key, value in data.items():
                self._add_xml_element(root, key, value)
        elif isinstance(data, list):
            for i, item in enumerate(data):
                self._add_xml_element(root, 'item', item)
        else:
            root.text = str(data)
        
        return ET.tostring(root, encoding='unicode')
    
    def _add_xml_element(self, parent: ET.Element, name: str, value: Any):
        """添加XML元素"""
        element = ET.SubElement(parent, name)
        
        if isinstance(value, dict):
            for k, v in value.items():
                self._add_xml_element(element, k, v)
        elif isinstance(value, list):
            for item in value:
                self._add_xml_element(element, 'item', item)
        else:
            element.text = str(value)
    
    def _deserialize_from_xml(self, xml_string: str) -> Dict[str, Any]:
        """从XML反序列化"""
        root = ET.fromstring(xml_string)
        return self._xml_element_to_dict(root)
    
    def _xml_element_to_dict(self, element: ET.Element) -> Any:
        """XML元素转换为字典"""
        if len(element) == 0:
            return element.text
        
        result = {}
        for child in element:
            child_data = self._xml_element_to_dict(child)
            
            if child.tag in result:
                if not isinstance(result[child.tag], list):
                    result[child.tag] = [result[child.tag]]
                result[child.tag].append(child_data)
            else:
                result[child.tag] = child_data
        
        return result
    
    def _serialize_to_csv(self, data: List[Dict[str, Any]], **kwargs) -> str:
        """序列化为CSV"""
        if not data:
            return ""
        
        output = []
        fieldnames = kwargs.get('fieldnames') or list(data[0].keys())
        
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
        
        return '\n'.join(output)
    
    def _deserialize_from_csv(self, csv_string: str) -> List[Dict[str, Any]]:
        """从CSV反序列化"""
        reader = csv.DictReader(csv_string.splitlines())
        return list(reader)
    
    def get_serialization_stats(self) -> Dict[str, Any]:
        """
        获取序列化统计
        
        Returns:
            序列化统计
        """
        return {
            'total_serializations': len(self.serialization_history)
        }


def main():
    """主函数 - 示例用法"""
    serializer = DataSerialization()
    
    # 序列化数据
    data = {'key1': 'value1', 'key2': 'value2'}
    json_data = serializer.serialize(data, SerializationFormat.JSON)
    print(f"JSON序列化: {json_data}")
    
    # 反序列化数据
    deserialized = serializer.deserialize(json_data, SerializationFormat.JSON)
    print(f"JSON反序列化: {deserialized}")
    
    # 格式转换
    xml_data = serializer.convert_format(data, SerializationFormat.JSON, SerializationFormat.XML)
    print(f"XML转换: {xml_data[:100]}...")


if __name__ == '__main__':
    main()
