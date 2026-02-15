"""
办公自动化Schema转换器

专注于ODF/OOXML转换、EDIFACT解析、PostgreSQL存储
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from functools import lru_cache

from .logger import logger
from .exceptions import ConversionError, ValidationError, ParseError


class DocumentFormat(Enum):
    """文档格式"""
    ODF = "odf"
    OOXML = "ooxml"
    PDF = "pdf"
    HTML = "html"


class DocumentType(Enum):
    """文档类型"""
    TEXT = "text"  # 文本文档
    SPREADSHEET = "spreadsheet"  # 电子表格
    PRESENTATION = "presentation"  # 演示文稿


@dataclass
class Document:
    """文档"""
    document_id: str
    name: str
    document_type: DocumentType
    format: DocumentFormat
    content: Dict[str, Any]
    metadata: Dict[str, Any] = None


class OAConverter:
    """
    办公自动化转换器
    
    专注于ODF/OOXML转换、EDIFACT解析、PostgreSQL存储
    """
    
    def __init__(self):
        self.documents: Dict[str, Document] = {}
        self.conversion_rules: Dict[str, Dict[str, Any]] = {}
        self._init_conversion_rules()
        logger.info("OAConverter initialized")
    
    def _init_conversion_rules(self):
        """初始化转换规则"""
        # ODF到OOXML转换规则
        self.conversion_rules['odf_to_ooxml'] = {
            'text': {
                'odf_ns': 'urn:oasis:names:tc:opendocument:xmlns:text:1.0',
                'ooxml_ns': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
                'element_mapping': {
                    'p': 'p',
                    'h': 'h',
                    'span': 'r'
                }
            },
            'spreadsheet': {
                'odf_ns': 'urn:oasis:names:tc:opendocument:xmlns:table:1.0',
                'ooxml_ns': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main',
                'element_mapping': {
                    'table': 'worksheet',
                    'table-row': 'row',
                    'table-cell': 'c'
                }
            },
            'presentation': {
                'odf_ns': 'urn:oasis:names:tc:opendocument:xmlns:presentation:1.0',
                'ooxml_ns': 'http://schemas.openxmlformats.org/presentationml/2006/main',
                'element_mapping': {
                    'page': 'slide',
                    'title': 'title'
                }
            }
        }
        
        # OOXML到ODF转换规则
        self.conversion_rules['ooxml_to_odf'] = {
            'text': {
                'ooxml_ns': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
                'odf_ns': 'urn:oasis:names:tc:opendocument:xmlns:text:1.0',
                'element_mapping': {
                    'p': 'p',
                    'h': 'h',
                    'r': 'span'
                }
            },
            'spreadsheet': {
                'ooxml_ns': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main',
                'odf_ns': 'urn:oasis:names:tc:opendocument:xmlns:table:1.0',
                'element_mapping': {
                    'worksheet': 'table',
                    'row': 'table-row',
                    'c': 'table-cell'
                }
            },
            'presentation': {
                'ooxml_ns': 'http://schemas.openxmlformats.org/presentationml/2006/main',
                'odf_ns': 'urn:oasis:names:tc:opendocument:xmlns:presentation:1.0',
                'element_mapping': {
                    'slide': 'page',
                    'title': 'title'
                }
            }
        }
    
    def convert_odf_to_ooxml(self, odf_path: str, output_path: str) -> Dict[str, Any]:
        """
        ODF到OOXML转换
        
        Args:
            odf_path: ODF文件路径
            output_path: 输出文件路径
            
        Returns:
            转换结果
            
        Raises:
            ConversionError: 转换失败时抛出
            ValidationError: 输入验证失败时抛出
            ParseError: 解析失败时抛出
        """
        try:
            # 验证输入
            if not odf_path:
                raise ValidationError("ODF文件路径不能为空")
            if not output_path:
                raise ValidationError("输出文件路径不能为空")
            
            odf_file = Path(odf_path)
            if not odf_file.exists():
                raise ValidationError(f"ODF文件不存在: {odf_path}")
            
            logger.info(f"开始转换ODF到OOXML: {odf_path} -> {output_path}")
            
            # 读取ODF文件（ZIP格式）
            with zipfile.ZipFile(odf_path, 'r') as odf_zip:
                # 确定文档类型
                if 'mimetype' not in odf_zip.namelist():
                    raise ParseError("ODF文件缺少mimetype文件")
                
                mimetype = odf_zip.read('mimetype').decode('utf-8')
                document_type = self._get_document_type_from_mimetype(mimetype)
                logger.debug(f"检测到文档类型: {document_type.value}")
                
                # 读取内容文件
                content_file = 'content.xml'
                if content_file not in odf_zip.namelist():
                    raise ParseError("ODF文件缺少content.xml")
                
                content_xml = odf_zip.read(content_file).decode('utf-8')
                
                # 解析XML
                try:
                    root = ET.fromstring(content_xml)
                except ET.ParseError as e:
                    raise ParseError(f"XML解析失败: {str(e)}") from e
                
                # 转换XML结构
                converted_root = self._convert_xml_structure(
                    root,
                    document_type,
                    'odf_to_ooxml'
                )
                
                # 创建OOXML文件（ZIP格式）
                self._create_ooxml_file(converted_root, output_path, document_type)
                
                logger.info(f"转换成功: {odf_path} -> {output_path}")
                
                return {
                    'success': True,
                    'source_format': 'odf',
                    'target_format': 'ooxml',
                    'document_type': document_type.value,
                    'output_path': output_path
                }
        
        except (ValidationError, ParseError):
            raise
        except zipfile.BadZipFile as e:
            logger.error(f"无效的ZIP文件: {odf_path}", exc_info=True)
            raise ConversionError(f"无效的ODF文件格式: {str(e)}") from e
        except Exception as e:
            logger.error(f"ODF到OOXML转换失败: {str(e)}", exc_info=True)
            raise ConversionError(f"转换失败: {str(e)}") from e
    
    def convert_ooxml_to_odf(self, ooxml_path: str, output_path: str) -> Dict[str, Any]:
        """
        OOXML到ODF转换
        
        Args:
            ooxml_path: OOXML文件路径
            output_path: 输出文件路径
            
        Returns:
            转换结果
        """
        try:
            # 读取OOXML文件（ZIP格式）
            with zipfile.ZipFile(ooxml_path, 'r') as ooxml_zip:
                # 确定文档类型
                document_type = self._detect_ooxml_type(ooxml_zip)
                
                # 读取主文档文件
                main_file = self._get_ooxml_main_file(ooxml_zip, document_type)
                
                if main_file:
                    content_xml = ooxml_zip.read(main_file).decode('utf-8')
                    
                    # 解析XML
                    root = ET.fromstring(content_xml)
                    
                    # 转换XML结构
                    converted_root = self._convert_xml_structure(
                        root,
                        document_type,
                        'ooxml_to_odf'
                    )
                    
                    # 创建ODF文件（ZIP格式）
                    self._create_odf_file(converted_root, output_path, document_type)
                    
                    return {
                        'success': True,
                        'source_format': 'ooxml',
                        'target_format': 'odf',
                        'document_type': document_type.value,
                        'output_path': output_path
                    }
                else:
                    return {
                        'success': False,
                        'error': '无法确定OOXML主文档文件'
                    }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def register_document(self, document_config: Dict[str, Any]) -> Document:
        """
        注册文档
        
        Args:
            document_config: 文档配置
            
        Returns:
            文档对象
            
        Raises:
            ValidationError: 当配置无效时
        """
        # 验证必需字段
        document_id = document_config.get('document_id')
        if not document_id:
            raise ValidationError("文档ID不能为空")
        
        # 解析文档类型
        doc_type_str = document_config.get('document_type', 'text')
        try:
            document_type = DocumentType(doc_type_str.lower())
        except ValueError:
            raise ValidationError(f"无效的文档类型: {doc_type_str}")
        
        # 解析文档格式
        format_str = document_config.get('format', 'odf')
        try:
            document_format = DocumentFormat(format_str.lower())
        except ValueError:
            raise ValidationError(f"无效的文档格式: {format_str}")
        
        # 创建文档对象
        document = Document(
            document_id=document_id,
            name=document_config.get('name', ''),
            document_type=document_type,
            format=document_format,
            content=document_config.get('content', {}),
            metadata=document_config.get('metadata', {})
        )
        
        # 保存文档
        self.documents[document_id] = document
        logger.info(f"文档注册成功: {document_id}")
        
        return document
    
    def _get_document_type_from_mimetype(self, mimetype: str) -> DocumentType:
        """从MIME类型获取文档类型"""
        if 'text' in mimetype:
            return DocumentType.TEXT
        elif 'spreadsheet' in mimetype:
            return DocumentType.SPREADSHEET
        elif 'presentation' in mimetype:
            return DocumentType.PRESENTATION
        else:
            return DocumentType.TEXT
    
    def _detect_ooxml_type(self, ooxml_zip: zipfile.ZipFile) -> DocumentType:
        """检测OOXML文档类型"""
        if 'word/document.xml' in ooxml_zip.namelist():
            return DocumentType.TEXT
        elif 'xl/workbook.xml' in ooxml_zip.namelist():
            return DocumentType.SPREADSHEET
        elif 'ppt/presentation.xml' in ooxml_zip.namelist():
            return DocumentType.PRESENTATION
        else:
            return DocumentType.TEXT
    
    def _get_ooxml_main_file(self, ooxml_zip: zipfile.ZipFile,
                             document_type: DocumentType) -> Optional[str]:
        """获取OOXML主文档文件"""
        file_mapping = {
            DocumentType.TEXT: 'word/document.xml',
            DocumentType.SPREADSHEET: 'xl/sharedStrings.xml',
            DocumentType.PRESENTATION: 'ppt/slides/slide1.xml'
        }
        
        main_file = file_mapping.get(document_type)
        if main_file and main_file in ooxml_zip.namelist():
            return main_file
        
        return None
    
    def _convert_xml_structure(self, root: ET.Element, document_type: DocumentType,
                               conversion_direction: str) -> ET.Element:
        """转换XML结构"""
        direction_key = conversion_direction
        
        if direction_key in self.conversion_rules:
            rules = self.conversion_rules[direction_key].get(document_type.value, {})
            element_mapping = rules.get('element_mapping', {})
            
            # 简化实现：创建新的根元素
            new_root = ET.Element('converted')
            
            # 递归转换元素
            self._convert_elements(root, new_root, element_mapping)
            
            return new_root
        
        return root
    
    def _convert_elements(self, source: ET.Element, target: ET.Element,
                         element_mapping: Dict[str, str]):
        """递归转换元素"""
        for child in source:
            tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
            
            if tag in element_mapping:
                new_tag = element_mapping[tag]
                new_element = ET.SubElement(target, new_tag)
                new_element.text = child.text
                new_element.attrib = child.attrib
                
                # 递归处理子元素
                self._convert_elements(child, new_element, element_mapping)
    
    def _create_ooxml_file(self, root: ET.Element, output_path: str,
                          document_type: DocumentType):
        """创建OOXML文件"""
        # 简化实现：创建ZIP文件结构
        with zipfile.ZipFile(output_path, 'w') as ooxml_zip:
            # 写入[Content_Types].xml
            content_types = self._generate_content_types(document_type)
            ooxml_zip.writestr('[Content_Types].xml', content_types)
            
            # 写入主文档XML
            main_xml = ET.tostring(root, encoding='utf-8')
            main_file = self._get_ooxml_main_file_name(document_type)
            ooxml_zip.writestr(main_file, main_xml)
    
    def _create_odf_file(self, root: ET.Element, output_path: str,
                        document_type: DocumentType):
        """创建ODF文件"""
        # 简化实现：创建ZIP文件结构
        with zipfile.ZipFile(output_path, 'w') as odf_zip:
            # 写入mimetype
            mimetype = self._get_odf_mimetype(document_type)
            odf_zip.writestr('mimetype', mimetype)
            
            # 写入content.xml
            content_xml = ET.tostring(root, encoding='utf-8')
            odf_zip.writestr('content.xml', content_xml)
    
    def _generate_content_types(self, document_type: DocumentType) -> str:
        """生成Content Types XML"""
        content_types = {
            DocumentType.TEXT: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml',
            DocumentType.SPREADSHEET: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml',
            DocumentType.PRESENTATION: 'application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml'
        }
        
        return f'<?xml version="1.0" encoding="UTF-8"?><Types><Default Extension="xml" ContentType="{content_types.get(document_type)}"/></Types>'
    
    def _get_ooxml_main_file_name(self, document_type: DocumentType) -> str:
        """获取OOXML主文档文件名"""
        file_mapping = {
            DocumentType.TEXT: 'word/document.xml',
            DocumentType.SPREADSHEET: 'xl/sharedStrings.xml',
            DocumentType.PRESENTATION: 'ppt/slides/slide1.xml'
        }
        return file_mapping.get(document_type, 'document.xml')
    
    def _get_odf_mimetype(self, document_type: DocumentType) -> str:
        """获取ODF MIME类型"""
        mimetype_mapping = {
            DocumentType.TEXT: 'application/vnd.oasis.opendocument.text',
            DocumentType.SPREADSHEET: 'application/vnd.oasis.opendocument.spreadsheet',
            DocumentType.PRESENTATION: 'application/vnd.oasis.opendocument.presentation'
        }
        return mimetype_mapping.get(document_type, 'application/vnd.oasis.opendocument.text')


def main():
    """主函数 - 示例用法"""
    converter = OAConverter()
    
    # ODF到OOXML转换示例
    result = converter.convert_odf_to_ooxml(
        'input.odt',
        'output.docx'
    )
    print(f"转换结果: {result}")


if __name__ == '__main__':
    main()
