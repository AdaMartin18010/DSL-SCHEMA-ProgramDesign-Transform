"""
数据格式转换模块

专注于数据格式转换、格式检测、格式验证
"""

from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import json
import csv
import xml.etree.ElementTree as ET
import logging
import re

logger = logging.getLogger(__name__)


class DataFormat(Enum):
    """数据格式"""
    JSON = "json"
    XML = "xml"
    CSV = "csv"
    TSV = "tsv"
    EXCEL = "excel"
    PARQUET = "parquet"
    AVRO = "avro"
    PROTOBUF = "protobuf"
    YAML = "yaml"
    TOML = "toml"


@dataclass
class FormatConversionResult:
    """格式转换结果"""
    source_format: DataFormat
    target_format: DataFormat
    converted_data: Union[str, bytes]
    conversion_time: float
    success: bool
    error: Optional[str] = None


class DataFormatConverter:
    """
    数据格式转换器
    
    专注于数据格式转换、格式检测、格式验证
    """
    
    def __init__(self):
        self.conversions: List[FormatConversionResult] = []
    
    def detect_format(self, data: Union[str, bytes]) -> Optional[DataFormat]:
        """
        检测数据格式
        
        Args:
            data: 数据
            
        Returns:
            检测到的格式
        """
        if isinstance(data, bytes):
            data_str = data.decode('utf-8', errors='ignore')
        else:
            data_str = data
        
        # 尝试JSON
        try:
            json.loads(data_str)
            return DataFormat.JSON
        except:
            pass
        
        # 尝试XML
        try:
            ET.fromstring(data_str)
            return DataFormat.XML
        except:
            pass
        
        # 尝试CSV
        try:
            lines = data_str.strip().split('\n')
            if len(lines) > 0:
                csv.Sniffer().sniff(lines[0])
                return DataFormat.CSV
        except:
            pass
        
        # 尝试TSV
        if '\t' in data_str and len(data_str.split('\n')) > 1:
            return DataFormat.TSV
        
        return None
    
    def convert_format(self, data: Union[str, bytes], source_format: DataFormat,
                      target_format: DataFormat) -> FormatConversionResult:
        """
        转换数据格式
        
        Args:
            data: 数据
            source_format: 源格式
            target_format: 目标格式
            
        Returns:
            转换结果
        """
        start_time = datetime.utcnow()
        
        try:
            # 先解析源格式
            parsed_data = self._parse_format(data, source_format)
            
            # 再序列化为目标格式
            converted_data = self._serialize_format(parsed_data, target_format)
            
            end_time = datetime.utcnow()
            conversion_time = (end_time - start_time).total_seconds()
            
            result = FormatConversionResult(
                source_format=source_format,
                target_format=target_format,
                converted_data=converted_data,
                conversion_time=conversion_time,
                success=True
            )
            
            self.conversions.append(result)
            return result
        
        except Exception as e:
            logger.error(f"格式转换失败: {e}")
            end_time = datetime.utcnow()
            conversion_time = (end_time - start_time).total_seconds()
            
            result = FormatConversionResult(
                source_format=source_format,
                target_format=target_format,
                converted_data=b'',
                conversion_time=conversion_time,
                success=False,
                error=str(e)
            )
            
            self.conversions.append(result)
            return result
    
    def _parse_format(self, data: Union[str, bytes], format_type: DataFormat) -> Any:
        """解析格式"""
        if isinstance(data, bytes):
            data_str = data.decode('utf-8')
        else:
            data_str = data
        
        if format_type == DataFormat.JSON:
            return json.loads(data_str)
        
        elif format_type == DataFormat.XML:
            root = ET.fromstring(data_str)
            return self._xml_to_dict(root)
        
        elif format_type == DataFormat.CSV:
            reader = csv.DictReader(data_str.splitlines())
            return list(reader)
        
        elif format_type == DataFormat.TSV:
            lines = data_str.strip().split('\n')
            if not lines:
                return []
            
            headers = lines[0].split('\t')
            result = []
            for line in lines[1:]:
                values = line.split('\t')
                result.append(dict(zip(headers, values)))
            return result
        
        else:
            raise ValueError(f"不支持的解析格式: {format_type}")
    
    def _serialize_format(self, data: Any, format_type: DataFormat) -> Union[str, bytes]:
        """序列化格式"""
        if format_type == DataFormat.JSON:
            return json.dumps(data, ensure_ascii=False, indent=2)
        
        elif format_type == DataFormat.XML:
            return self._dict_to_xml(data)
        
        elif format_type == DataFormat.CSV:
            if not data:
                return ""
            
            if isinstance(data, list) and len(data) > 0:
                fieldnames = list(data[0].keys())
                output = []
                writer = csv.DictWriter(output, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
                return '\n'.join(output)
            else:
                return ""
        
        elif format_type == DataFormat.TSV:
            if not data:
                return ""
            
            if isinstance(data, list) and len(data) > 0:
                fieldnames = list(data[0].keys())
                lines = ['\t'.join(fieldnames)]
                for row in data:
                    values = [str(row.get(f, '')) for f in fieldnames]
                    lines.append('\t'.join(values))
                return '\n'.join(lines)
            else:
                return ""
        
        else:
            raise ValueError(f"不支持的序列化格式: {format_type}")
    
    def _xml_to_dict(self, element: ET.Element) -> Any:
        """XML转换为字典"""
        if len(element) == 0:
            return element.text
        
        result = {}
        for child in element:
            child_data = self._xml_to_dict(child)
            
            if child.tag in result:
                if not isinstance(result[child.tag], list):
                    result[child.tag] = [result[child.tag]]
                result[child.tag].append(child_data)
            else:
                result[child.tag] = child_data
        
        return result
    
    def _dict_to_xml(self, data: Any, root_name: str = 'root') -> str:
        """字典转换为XML"""
        root = ET.Element(root_name)
        
        if isinstance(data, dict):
            for key, value in data.items():
                self._add_xml_element(root, key, value)
        elif isinstance(data, list):
            for item in data:
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
    
    def validate_format(self, data: Union[str, bytes], format_type: DataFormat) -> Dict[str, Any]:
        """
        验证数据格式
        
        Args:
            data: 数据
            format_type: 格式类型
            
        Returns:
            验证结果
        """
        try:
            self._parse_format(data, format_type)
            return {
                'valid': True,
                'format': format_type.value,
                'error': None
            }
        except Exception as e:
            return {
                'valid': False,
                'format': format_type.value,
                'error': str(e)
            }
    
    def get_conversion_stats(self) -> Dict[str, Any]:
        """
        获取转换统计
        
        Returns:
            转换统计
        """
        total_conversions = len(self.conversions)
        successful_conversions = sum(1 for c in self.conversions if c.success)
        failed_conversions = total_conversions - successful_conversions
        
        if total_conversions > 0:
            avg_time = sum(c.conversion_time for c in self.conversions) / total_conversions
        else:
            avg_time = 0.0
        
        return {
            'total_conversions': total_conversions,
            'successful_conversions': successful_conversions,
            'failed_conversions': failed_conversions,
            'success_rate': (successful_conversions / total_conversions * 100) if total_conversions > 0 else 0.0,
            'average_conversion_time': avg_time
        }


def main():
    """主函数 - 示例用法"""
    converter = DataFormatConverter()
    
    # 检测格式
    json_data = '{"key": "value"}'
    detected_format = converter.detect_format(json_data)
    print(f"检测到的格式: {detected_format.value if detected_format else None}")
    
    # 转换格式
    result = converter.convert_format(json_data, DataFormat.JSON, DataFormat.XML)
    print(f"转换结果: 成功={result.success}, 时间={result.conversion_time:.3f}秒")


if __name__ == '__main__':
    main()
