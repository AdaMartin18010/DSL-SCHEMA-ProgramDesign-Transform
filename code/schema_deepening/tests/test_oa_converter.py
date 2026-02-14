"""
OA转换器测试

测试OAConverter的核心功能
"""

import unittest
import sys
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from schema_deepening import OAConverter, DocumentFormat, DocumentType
from schema_deepening.exceptions import ConversionError, ValidationError, ParseError


class TestOAConverter(unittest.TestCase):
    """OA转换器测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.converter = OAConverter()
    
    def test_convert_odf_to_ooxml_empty_path(self):
        """测试空路径"""
        with self.assertRaises(ValidationError):
            self.converter.convert_odf_to_ooxml("", "output.docx")
    
    def test_convert_odf_to_ooxml_nonexistent_file(self):
        """测试不存在的文件"""
        with self.assertRaises(ValidationError):
            self.converter.convert_odf_to_ooxml("nonexistent.odt", "output.docx")
    
    def test_detect_document_type_text(self):
        """测试检测文本文档类型"""
        mimetype = "application/vnd.oasis.opendocument.text"
        doc_type = self.converter._get_document_type_from_mimetype(mimetype)
        self.assertEqual(doc_type, DocumentType.TEXT)
    
    def test_detect_document_type_spreadsheet(self):
        """测试检测电子表格类型"""
        mimetype = "application/vnd.oasis.opendocument.spreadsheet"
        doc_type = self.converter._get_document_type_from_mimetype(mimetype)
        self.assertEqual(doc_type, DocumentType.SPREADSHEET)
    
    def test_detect_document_type_presentation(self):
        """测试检测演示文稿类型"""
        mimetype = "application/vnd.oasis.opendocument.presentation"
        doc_type = self.converter._get_document_type_from_mimetype(mimetype)
        self.assertEqual(doc_type, DocumentType.PRESENTATION)
    
    def test_register_document(self):
        """测试注册文档"""
        document_config = {
            'document_id': 'doc_1',
            'name': '测试文档',
            'document_type': 'text',
            'format': 'odf',
            'content': {'text': '测试内容'}
        }
        
        document = self.converter.register_document(document_config)
        
        self.assertEqual(document.document_id, 'doc_1')
        self.assertEqual(document.name, '测试文档')
        self.assertEqual(document.document_type, DocumentType.TEXT)
        self.assertEqual(document.format, DocumentFormat.ODF)
        self.assertIn('doc_1', self.converter.documents)
    
    def test_register_document_invalid_type(self):
        """测试无效文档类型"""
        document_config = {
            'document_id': 'doc_1',
            'document_type': 'invalid_type',
            'format': 'odf'
        }
        
        with self.assertRaises(ValidationError):
            self.converter.register_document(document_config)
    
    def test_register_document_invalid_format(self):
        """测试无效格式"""
        document_config = {
            'document_id': 'doc_1',
            'document_type': 'text',
            'format': 'invalid_format'
        }
        
        with self.assertRaises(ValidationError):
            self.converter.register_document(document_config)


if __name__ == '__main__':
    unittest.main()
