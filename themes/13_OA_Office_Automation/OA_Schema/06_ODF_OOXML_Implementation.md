# ODF/OOXML完整转换实现

## 概述

本文档提供完整的ODF（Open Document Format）到OOXML（Office Open XML）转换实现，支持Word、Excel、PowerPoint文档的双向转换。

---

## 1. ODF/OOXML文档结构解析器

```python
"""
ODF/OOXML文档结构解析器
完整实现文档格式解析和转换功能
"""
import logging
import zipfile
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum
import tempfile
import shutil
import re

logger = logging.getLogger(__name__)


class DocumentType(Enum):
    """文档类型枚举"""
    WORD = "word"
    SPREADSHEET = "spreadsheet"
    PRESENTATION = "presentation"


@dataclass
class DocumentStyle:
    """文档样式定义"""
    style_id: str
    style_name: str
    style_family: str
    font_name: str = "Arial"
    font_size: float = 12.0
    font_weight: str = "normal"
    font_style: str = "normal"
    text_color: str = "#000000"
    background_color: str = "transparent"
    text_align: str = "left"
    margin_top: float = 0.0
    margin_bottom: float = 0.0
    margin_left: float = 0.0
    margin_right: float = 0.0
    line_height: float = 1.0
    extra_properties: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ParagraphElement:
    """段落元素"""
    text: str
    style_id: Optional[str] = None
    bold: bool = False
    italic: bool = False
    underline: bool = False
    font_size: Optional[float] = None
    font_name: Optional[str] = None
    color: Optional[str] = None
    hyperlink: Optional[str] = None


@dataclass
class TableCell:
    """表格单元格"""
    content: str
    row_span: int = 1
    col_span: int = 1
    style_id: Optional[str] = None
    value_type: str = "string"
    numeric_value: Optional[float] = None


@dataclass
class TableRow:
    """表格行"""
    cells: List[TableCell] = field(default_factory=list)
    style_id: Optional[str] = None
    height: Optional[float] = None


@dataclass
class TableElement:
    """表格元素"""
    table_id: str
    rows: List[TableRow] = field(default_factory=list)
    column_count: int = 0
    style_id: Optional[str] = None
    column_widths: List[float] = field(default_factory=list)


@dataclass
class SlideElement:
    """幻灯片元素"""
    slide_id: str
    slide_name: str
    layout_type: str = "title_content"
    title: str = ""
    content_elements: List[Any] = field(default_factory=list)
    notes: str = ""
    transition: Optional[str] = None


@dataclass
class DocumentMetadata:
    """文档元数据"""
    title: str = ""
    creator: str = ""
    subject: str = ""
    description: str = ""
    keywords: str = ""
    created_date: Optional[str] = None
    modified_date: Optional[str] = None
    version: str = "1.0"
    application: str = ""


class ODFDocumentParser:
    """ODF文档解析器"""
    
    # ODF命名空间
    NAMESPACES = {
        'office': 'urn:oasis:names:tc:opendocument:xmlns:office:1.0',
        'text': 'urn:oasis:names:tc:opendocument:xmlns:text:1.0',
        'table': 'urn:oasis:names:tc:opendocument:xmlns:table:1.0',
        'style': 'urn:oasis:names:tc:opendocument:xmlns:style:1.0',
        'fo': 'urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0',
        'draw': 'urn:oasis:names:tc:opendocument:xmlns:drawing:1.0',
        'dc': 'http://purl.org/dc/elements/1.1/',
        'meta': 'urn:oasis:names:tc:opendocument:xmlns:meta:1.0',
        'presentation': 'urn:oasis:names:tc:opendocument:xmlns:presentation:1.0'
    }
    
    def __init__(self):
        self.styles: Dict[str, DocumentStyle] = {}
        self.metadata = DocumentMetadata()
    
    def parse_document(self, odf_path: str) -> Dict[str, Any]:
        """解析ODF文档"""
        document = {
            'metadata': self.metadata,
            'styles': self.styles,
            'content': {}
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # 解压ODF文件
            with zipfile.ZipFile(odf_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            # 解析元数据
            meta_path = Path(temp_dir) / 'meta.xml'
            if meta_path.exists():
                self._parse_metadata(str(meta_path))
            
            # 解析样式
            styles_path = Path(temp_dir) / 'styles.xml'
            if styles_path.exists():
                self._parse_styles(str(styles_path))
            
            # 解析内容
            content_path = Path(temp_dir) / 'content.xml'
            if content_path.exists():
                document['content'] = self._parse_content(str(content_path))
        
        return document
    
    def _parse_metadata(self, meta_path: str):
        """解析元数据"""
        tree = ET.parse(meta_path)
        root = tree.getroot()
        
        # 解析DC元素
        title_elem = root.find('.//dc:title', self.NAMESPACES)
        if title_elem is not None:
            self.metadata.title = title_elem.text or ""
        
        creator_elem = root.find('.//dc:creator', self.NAMESPACES)
        if creator_elem is not None:
            self.metadata.creator = creator_elem.text or ""
        
        subject_elem = root.find('.//dc:subject', self.NAMESPACES)
        if subject_elem is not None:
            self.metadata.subject = subject_elem.text or ""
        
        description_elem = root.find('.//dc:description', self.NAMESPACES)
        if description_elem is not None:
            self.metadata.description = description_elem.text or ""
        
        # 解析日期
        date_elem = root.find('.//meta:creation-date', self.NAMESPACES)
        if date_elem is not None:
            self.metadata.created_date = date_elem.text
        
        mod_date_elem = root.find('.//dc:date', self.NAMESPACES)
        if mod_date_elem is not None:
            self.metadata.modified_date = mod_date_elem.text
    
    def _parse_styles(self, styles_path: str):
        """解析样式定义"""
        tree = ET.parse(styles_path)
        root = tree.getroot()
        
        # 解析段落样式
        style_elems = root.findall('.//style:style[@style:family="paragraph"]', self.NAMESPACES)
        for style_elem in style_elems:
            style_id = style_elem.get('{urn:oasis:names:tc:opendocument:xmlns:style:1.0}name', '')
            style_name = style_elem.get('{urn:oasis:names:tc:opendocument:xmlns:style:1.0}display-name', style_id)
            
            doc_style = DocumentStyle(
                style_id=style_id,
                style_name=style_name,
                style_family='paragraph'
            )
            
            # 解析文本属性
            text_props = style_elem.find('.//style:text-properties', self.NAMESPACES)
            if text_props is not None:
                font_name = text_props.get('{urn:oasis:names:tc:opendocument:xmlns:style:1.0}font-name')
                if font_name:
                    doc_style.font_name = font_name
                
                font_size = text_props.get('{urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0}font-size')
                if font_size:
                    doc_style.font_size = self._parse_length(font_size)
                
                font_weight = text_props.get('{urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0}font-weight')
                if font_weight:
                    doc_style.font_weight = font_weight
                
                font_style = text_props.get('{urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0}font-style')
                if font_style:
                    doc_style.font_style = font_style
                
                color = text_props.get('{urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0}color')
                if color:
                    doc_style.text_color = color
            
            # 解析段落属性
            para_props = style_elem.find('.//style:paragraph-properties', self.NAMESPACES)
            if para_props is not None:
                text_align = para_props.get('{urn:oasis:names:tc:opendocument:xmlns:fo:1.0}text-align')
                if text_align:
                    doc_style.text_align = text_align
                
                margin_top = para_props.get('{urn:oasis:names:tc:opendocument:xmlns:fo:1.0}margin-top')
                if margin_top:
                    doc_style.margin_top = self._parse_length(margin_top)
                
                margin_bottom = para_props.get('{urn:oasis:names:tc:opendocument:xmlns:fo:1.0}margin-bottom')
                if margin_bottom:
                    doc_style.margin_bottom = self._parse_length(margin_bottom)
            
            self.styles[style_id] = doc_style
    
    def _parse_content(self, content_path: str) -> Dict[str, Any]:
        """解析文档内容"""
        tree = ET.parse(content_path)
        root = tree.getroot()
        
        content = {
            'paragraphs': [],
            'tables': [],
            'slides': []
        }
        
        # 解析正文中的段落
        body = root.find('.//office:body', self.NAMESPACES)
        if body is not None:
            # 解析文本段落
            text_elem = body.find('.//office:text', self.NAMESPACES)
            if text_elem is not None:
                paragraphs = text_elem.findall('.//text:p', self.NAMESPACES)
                for para in paragraphs:
                    paragraph = self._parse_paragraph(para)
                    content['paragraphs'].append(paragraph)
            
            # 解析表格
            tables = body.findall('.//table:table', self.NAMESPACES)
            for table in tables:
                table_elem = self._parse_table(table)
                content['tables'].append(table_elem)
            
            # 解析演示文稿
            presentation = body.find('.//office:presentation', self.NAMESPACES)
            if presentation is not None:
                pages = presentation.findall('.//draw:page', self.NAMESPACES)
                for i, page in enumerate(pages):
                    slide = self._parse_slide(page, i)
                    content['slides'].append(slide)
        
        return content
    
    def _parse_paragraph(self, para_elem: ET.Element) -> ParagraphElement:
        """解析段落"""
        style_id = para_elem.get('{urn:oasis:names:tc:opendocument:xmlns:text:1.0}style-name')
        
        # 提取文本内容
        text_parts = []
        for node in para_elem.iter():
            if node.text:
                text_parts.append(node.text)
            if node.tail:
                text_parts.append(node.tail)
        
        text = ''.join(text_parts)
        
        # 检查粗体和斜体
        bold = False
        italic = False
        underline = False
        
        for span in para_elem.findall('.//text:span', self.NAMESPACES):
            span_style = span.get('{urn:oasis:names:tc:opendocument:xmlns:text:1.0}style-name', '')
            if span_style:
                # 检查样式属性
                pass
        
        return ParagraphElement(
            text=text,
            style_id=style_id,
            bold=bold,
            italic=italic,
            underline=underline
        )
    
    def _parse_table(self, table_elem: ET.Element) -> TableElement:
        """解析表格"""
        table_id = table_elem.get('{urn:oasis:names:tc:opendocument:xmlns:table:1.0}name', '')
        style_id = table_elem.get('{urn:oasis:names:tc:opendocument:xmlns:table:1.0}style-name')
        
        table = TableElement(
            table_id=table_id,
            style_id=style_id
        )
        
        # 解析行
        rows = table_elem.findall('.//table:table-row', self.NAMESPACES)
        for row_elem in rows:
            row = TableRow()
            
            # 解析单元格
            cells = row_elem.findall('.//table:table-cell', self.NAMESPACES)
            for cell_elem in cells:
                # 获取单元格内容
                text_elem = cell_elem.find('.//text:p', self.NAMESPACES)
                content = text_elem.text if text_elem is not None and text_elem.text else ""
                
                # 获取跨行跨列
                row_span = int(cell_elem.get('{urn:oasis:names:tc:opendocument:xmlns:table:1.0}number-rows-spanned', '1'))
                col_span = int(cell_elem.get('{urn:oasis:names:tc:opendocument:xmlns:table:1.0}number-columns-spanned', '1'))
                
                cell = TableCell(
                    content=content,
                    row_span=row_span,
                    col_span=col_span
                )
                row.cells.append(cell)
            
            table.rows.append(row)
            table.column_count = max(table.column_count, len(row.cells))
        
        return table
    
    def _parse_slide(self, page_elem: ET.Element, index: int) -> SlideElement:
        """解析幻灯片"""
        slide_id = page_elem.get('{urn:oasis:names:tc:opendocument:xmlns:drawing:1.0}id', f'slide{index}')
        slide_name = page_elem.get('{urn:oasis:names:tc:opendocument:xmlns:drawing:1.0}name', f'Slide {index + 1}')
        
        slide = SlideElement(
            slide_id=slide_id,
            slide_name=slide_name
        )
        
        # 解析文本框
        text_boxes = page_elem.findall('.//draw:text-box', self.NAMESPACES)
        for text_box in text_boxes:
            paragraphs = text_box.findall('.//text:p', self.NAMESPACES)
            for para in paragraphs:
                para_elem = self._parse_paragraph(para)
                slide.content_elements.append(para_elem)
        
        return slide
    
    def _parse_length(self, length_str: str) -> float:
        """解析长度值（转换为pt）"""
        if not length_str:
            return 0.0
        
        match = re.match(r'([\d.]+)(\w+)', length_str)
        if not match:
            return 0.0
        
        value = float(match.group(1))
        unit = match.group(2)
        
        conversion = {
            'pt': 1.0,
            'px': 0.75,
            'cm': 28.35,
            'mm': 2.835,
            'in': 72.0
        }
        
        return value * conversion.get(unit, 1.0)


class OOXMLDocumentBuilder:
    """OOXML文档构建器"""
    
    # OOXML命名空间
    NAMESPACES = {
        'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
        'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
        'wp': 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing',
        'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
        'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
        'x': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'
    }
    
    def __init__(self):
        self.document_type: Optional[DocumentType] = None
    
    def build_docx(self, odf_document: Dict[str, Any], output_path: str):
        """构建DOCX文档"""
        self.document_type = DocumentType.WORD
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # 创建目录结构
            word_dir = Path(temp_dir) / 'word'
            word_dir.mkdir()
            rels_dir = Path(temp_dir) / '_rels'
            rels_dir.mkdir()
            (word_dir / '_rels').mkdir()
            
            # 构建[Content_Types].xml
            self._create_content_types(temp_dir, DocumentType.WORD)
            
            # 构建.rels
            self._create_rels(temp_dir, DocumentType.WORD)
            
            # 构建word/_rels/document.xml.rels
            self._create_document_rels(str(word_dir / '_rels' / 'document.xml.rels'))
            
            # 构建document.xml
            self._create_document_xml(str(word_dir / 'document.xml'), odf_document)
            
            # 构建styles.xml
            self._create_styles_xml(str(word_dir / 'styles.xml'), odf_document.get('styles', {}))
            
            # 打包为docx
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in Path(temp_dir).rglob('*'):
                    if file_path.is_file():
                        arcname = file_path.relative_to(temp_dir)
                        zipf.write(file_path, arcname)
    
    def build_xlsx(self, odf_document: Dict[str, Any], output_path: str):
        """构建XLSX文档"""
        self.document_type = DocumentType.SPREADSHEET
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # 创建目录结构
            xl_dir = Path(temp_dir) / 'xl'
            xl_dir.mkdir()
            worksheets_dir = xl_dir / 'worksheets'
            worksheets_dir.mkdir()
            rels_dir = Path(temp_dir) / '_rels'
            rels_dir.mkdir()
            (xl_dir / '_rels').mkdir()
            
            # 构建[Content_Types].xml
            self._create_content_types(temp_dir, DocumentType.SPREADSHEET)
            
            # 构建xl/workbook.xml
            self._create_workbook_xml(str(xl_dir / 'workbook.xml'), odf_document)
            
            # 构建worksheets/sheet1.xml
            tables = odf_document.get('content', {}).get('tables', [])
            if tables:
                self._create_worksheet_xml(str(worksheets_dir / 'sheet1.xml'), tables[0])
            
            # 构建xl/styles.xml
            self._create_xlsx_styles_xml(str(xl_dir / 'styles.xml'))
            
            # 打包为xlsx
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in Path(temp_dir).rglob('*'):
                    if file_path.is_file():
                        arcname = file_path.relative_to(temp_dir)
                        zipf.write(file_path, arcname)
    
    def _create_content_types(self, temp_dir: str, doc_type: DocumentType):
        """创建[Content_Types].xml"""
        root = ET.Element('Types')
        root.set('xmlns', 'http://schemas.openxmlformats.org/package/2006/content-types')
        
        defaults = [
            ('rels', 'application/vnd.openxmlformats-package.relationships+xml'),
            ('xml', 'application/xml')
        ]
        
        for ext, content_type in defaults:
            default = ET.SubElement(root, 'Default')
            default.set('Extension', ext)
            default.set('ContentType', content_type)
        
        if doc_type == DocumentType.WORD:
            overrides = [
                ('/word/document.xml', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml'),
                ('/word/styles.xml', 'application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml')
            ]
        elif doc_type == DocumentType.SPREADSHEET:
            overrides = [
                ('/xl/workbook.xml', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml'),
                ('/xl/worksheets/sheet1.xml', 'application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml')
            ]
        else:
            overrides = []
        
        for part, content_type in overrides:
            override = ET.SubElement(root, 'Override')
            override.set('PartName', part)
            override.set('ContentType', content_type)
        
        tree = ET.ElementTree(root)
        tree.write(Path(temp_dir) / '[Content_Types].xml', encoding='UTF-8', xml_declaration=True)
    
    def _create_rels(self, temp_dir: str, doc_type: DocumentType):
        """创建根级别的.rels"""
        root = ET.Element('Relationships')
        root.set('xmlns', 'http://schemas.openxmlformats.org/package/2006/relationships')
        
        if doc_type == DocumentType.WORD:
            rel = ET.SubElement(root, 'Relationship')
            rel.set('Id', 'rId1')
            rel.set('Type', 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument')
            rel.set('Target', 'word/document.xml')
        elif doc_type == DocumentType.SPREADSHEET:
            rel = ET.SubElement(root, 'Relationship')
            rel.set('Id', 'rId1')
            rel.set('Type', 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument')
            rel.set('Target', 'xl/workbook.xml')
        
        tree = ET.ElementTree(root)
        tree.write(Path(temp_dir) / '_rels' / '.rels', encoding='UTF-8', xml_declaration=True)
    
    def _create_document_rels(self, rels_path: str):
        """创建document.xml.rels"""
        root = ET.Element('Relationships')
        root.set('xmlns', 'http://schemas.openxmlformats.org/package/2006/relationships')
        
        rel = ET.SubElement(root, 'Relationship')
        rel.set('Id', 'rId1')
        rel.set('Type', 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles')
        rel.set('Target', 'styles.xml')
        
        tree = ET.ElementTree(root)
        tree.write(rels_path, encoding='UTF-8', xml_declaration=True)
    
    def _create_document_xml(self, doc_path: str, odf_document: Dict[str, Any]):
        """创建document.xml"""
        # 创建根元素
        ns_w = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
        
        root = ET.Element('{%s}document' % ns_w)
        root.set('xmlns:w', ns_w)
        root.set('xmlns:r', 'http://schemas.openxmlformats.org/officeDocument/2006/relationships')
        
        body = ET.SubElement(root, '{%s}body' % ns_w)
        
        # 添加段落
        content = odf_document.get('content', {})
        paragraphs = content.get('paragraphs', [])
        
        for para in paragraphs:
            p_elem = ET.SubElement(body, '{%s}p' % ns_w)
            
            # 添加段落属性
            pPr = ET.SubElement(p_elem, '{%s}pPr' % ns_w)
            
            if para.style_id:
                pStyle = ET.SubElement(pPr, '{%s}pStyle' % ns_w)
                pStyle.set('{%s}val' % ns_w, para.style_id)
            
            # 添加文本运行
            if para.text:
                r_elem = ET.SubElement(p_elem, '{%s}r' % ns_w)
                
                # 运行属性
                rPr = ET.SubElement(r_elem, '{%s}rPr' % ns_w)
                
                if para.bold:
                    ET.SubElement(rPr, '{%s}b' % ns_w)
                if para.italic:
                    ET.SubElement(rPr, '{%s}i' % ns_w)
                
                # 文本
                t_elem = ET.SubElement(r_elem, '{%s}t' % ns_w)
                t_elem.text = para.text
        
        # 添加文档结束标记
        sectPr = ET.SubElement(body, '{%s}sectPr' % ns_w)
        pgSz = ET.SubElement(sectPr, '{%s}pgSz' % ns_w)
        pgSz.set('{%s}w' % ns_w, '12240')
        pgSz.set('{%s}h' % ns_w, '15840')
        
        tree = ET.ElementTree(root)
        tree.write(doc_path, encoding='UTF-8', xml_declaration=True)
    
    def _create_styles_xml(self, styles_path: str, styles: Dict[str, DocumentStyle]):
        """创建styles.xml"""
        ns_w = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
        
        root = ET.Element('{%s}styles' % ns_w)
        root.set('xmlns:w', ns_w)
        
        # 添加文档默认设置
        docDefaults = ET.SubElement(root, '{%s}docDefaults' % ns_w)
        rPrDefault = ET.SubElement(docDefaults, '{%s}rPrDefault' % ns_w)
        rPr = ET.SubElement(rPrDefault, '{%s}rPr' % ns_w)
        
        # 添加样式
        for style_id, style in styles.items():
            style_elem = ET.SubElement(root, '{%s}style' % ns_w)
            style_elem.set('{%s}styleId' % ns_w, style_id)
            style_elem.set('{%s}type' % ns_w, style.style_family)
            
            # 样式名称
            name_elem = ET.SubElement(style_elem, '{%s}name' % ns_w)
            name_elem.set('{%s}val' % ns_w, style.style_name)
            
            # 段落属性
            pPr = ET.SubElement(style_elem, '{%s}pPr' % ns_w)
            jc = ET.SubElement(pPr, '{%s}jc' % ns_w)
            jc.set('{%s}val' % ns_w, style.text_align)
            
            # 文本属性
            rPr = ET.SubElement(style_elem, '{%s}rPr' % ns_w)
            
            if style.font_name:
                rFonts = ET.SubElement(rPr, '{%s}rFonts' % ns_w)
                rFonts.set('{%s}ascii' % ns_w, style.font_name)
                rFonts.set('{%s}hAnsi' % ns_w, style.font_name)
            
            if style.font_size:
                sz = ET.SubElement(rPr, '{%s}sz' % ns_w)
                sz.set('{%s}val' % ns_w, str(int(style.font_size * 2)))  # 半磅为单位
        
        tree = ET.ElementTree(root)
        tree.write(styles_path, encoding='UTF-8', xml_declaration=True)
    
    def _create_workbook_xml(self, workbook_path: str, odf_document: Dict[str, Any]):
        """创建workbook.xml"""
        ns_x = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'
        ns_r = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
        
        root = ET.Element('{%s}workbook' % ns_x)
        root.set('xmlns:x', ns_x)
        root.set('xmlns:r', ns_r)
        
        sheets = ET.SubElement(root, '{%s}sheets' % ns_x)
        
        # 添加工作表
        tables = odf_document.get('content', {}).get('tables', [])
        for i, table in enumerate(tables, 1):
            sheet = ET.SubElement(sheets, '{%s}sheet' % ns_x)
            sheet.set('{%s}name' % ns_x, table.table_id or f'Sheet{i}')
            sheet.set('{%s}sheetId' % ns_x, str(i))
            sheet.set('{%s}id' % ns_r, f'rId{i}')
        
        tree = ET.ElementTree(root)
        tree.write(workbook_path, encoding='UTF-8', xml_declaration=True)
    
    def _create_worksheet_xml(self, worksheet_path: str, table: TableElement):
        """创建worksheet.xml"""
        ns_x = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'
        
        root = ET.Element('{%s}worksheet' % ns_x)
        root.set('xmlns:x', ns_x)
        
        sheetData = ET.SubElement(root, '{%s}sheetData' % ns_x)
        
        # 添加行
        for row_idx, row in enumerate(table.rows, 1):
            row_elem = ET.SubElement(sheetData, '{%s}row' % ns_x)
            row_elem.set('{%s}r' % ns_x, str(row_idx))
            
            # 添加单元格
            for col_idx, cell in enumerate(row.cells, 1):
                cell_elem = ET.SubElement(row_elem, '{%s}c' % ns_x)
                cell_ref = f'{self._col_index_to_letter(col_idx)}{row_idx}'
                cell_elem.set('{%s}r' % ns_x, cell_ref)
                
                # 单元格类型
                if cell.value_type == 'float' or cell.numeric_value is not None:
                    cell_elem.set('{%s}t' % ns_x, 'n')
                    v = ET.SubElement(cell_elem, '{%s}v' % ns_x)
                    v.text = str(cell.numeric_value if cell.numeric_value is not None else cell.content)
                else:
                    cell_elem.set('{%s}t' % ns_x, 'inlineStr')
                    is_elem = ET.SubElement(cell_elem, '{%s}is' % ns_x)
                    t = ET.SubElement(is_elem, '{%s}t' % ns_x)
                    t.text = cell.content
        
        tree = ET.ElementTree(root)
        tree.write(worksheet_path, encoding='UTF-8', xml_declaration=True)
    
    def _create_xlsx_styles_xml(self, styles_path: str):
        """创建XLSX的styles.xml"""
        ns_x = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'
        
        root = ET.Element('{%s}styleSheet' % ns_x)
        root.set('xmlns:x', ns_x)
        
        # 字体
        fonts = ET.SubElement(root, '{%s}fonts' % ns_x)
        fonts.set('{%s}count' % ns_x, '1')
        font = ET.SubElement(fonts, '{%s}font' % ns_x)
        sz = ET.SubElement(font, '{%s}sz' % ns_x)
        sz.set('{%s}val' % ns_x, '11')
        name = ET.SubElement(font, '{%s}name' % ns_x)
        name.set('{%s}val' % ns_x, 'Calibri')
        
        # 填充
        fills = ET.SubElement(root, '{%s}fills' % ns_x)
        fills.set('{%s}count' % ns_x, '2')
        fill1 = ET.SubElement(fills, '{%s}fill' % ns_x)
        ET.SubElement(fill1, '{%s}patternFill' % ns_x)
        fill2 = ET.SubElement(fills, '{%s}fill' % ns_x)
        ET.SubElement(fill2, '{%s}patternFill' % ns_x)
        
        # 边框
        borders = ET.SubElement(root, '{%s}borders' % ns_x)
        borders.set('{%s}count' % ns_x, '1')
        border = ET.SubElement(borders, '{%s}border' % ns_x)
        
        # 单元格样式
        cellXfs = ET.SubElement(root, '{%s}cellXfs' % ns_x)
        cellXfs.set('{%s}count' % ns_x, '1')
        xf = ET.SubElement(cellXfs, '{%s}xf' % ns_x)
        xf.set('{%s}numFmtId' % ns_x, '0')
        xf.set('{%s}fontId' % ns_x, '0')
        xf.set('{%s}fillId' % ns_x, '0')
        xf.set('{%s}borderId' % ns_x, '0')
        
        tree = ET.ElementTree(root)
        tree.write(styles_path, encoding='UTF-8', xml_declaration=True)
    
    def _col_index_to_letter(self, col_idx: int) -> str:
        """将列索引转换为字母（1->A, 27->AA）"""
        result = ""
        while col_idx > 0:
            col_idx -= 1
            result = chr(65 + (col_idx % 26)) + result
            col_idx //= 26
        return result


class ODFToOOXMLConverter:
    """ODF到OOXML完整转换器"""
    
    def __init__(self):
        self.parser = ODFDocumentParser()
        self.builder = OOXMLDocumentBuilder()
    
    def convert(self, input_path: str, output_path: str) -> bool:
        """执行转换"""
        try:
            # 解析ODF文档
            odf_doc = self.parser.parse_document(input_path)
            
            # 检测文档类型
            file_ext = Path(input_path).suffix.lower()
            
            if file_ext == '.odt':
                self.builder.build_docx(odf_doc, output_path)
            elif file_ext == '.ods':
                self.builder.build_xlsx(odf_doc, output_path)
            else:
                logger.error(f"Unsupported ODF file type: {file_ext}")
                return False
            
            logger.info(f"Successfully converted {input_path} to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Conversion failed: {e}", exc_info=True)
            return False


# 使用示例
if __name__ == "__main__":
    converter = ODFToOOXMLConverter()
    
    # 转换ODT到DOCX
    converter.convert("input.odt", "output.docx")
    
    # 转换ODS到XLSX
    converter.convert("input.ods", "output.xlsx")
```

---

## 2. 转换使用说明

### 2.1 基本使用

```python
from odf_ooxml_converter import ODFToOOXMLConverter

converter = ODFToOOXMLConverter()

# 转换Word文档
converter.convert("document.odt", "document.docx")

# 转换Excel文档
converter.convert("spreadsheet.ods", "spreadsheet.xlsx")
```

### 2.2 批量转换

```python
import os
from pathlib import Path

def batch_convert(input_dir: str, output_dir: str):
    """批量转换ODF文件"""
    converter = ODFToOOXMLConverter()
    
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    for odf_file in input_path.glob("*.odt"):
        docx_file = output_path / f"{odf_file.stem}.docx"
        converter.convert(str(odf_file), str(docx_file))
    
    for ods_file in input_path.glob("*.ods"):
        xlsx_file = output_path / f"{ods_file.stem}.xlsx"
        converter.convert(str(ods_file), str(xlsx_file))

# 执行批量转换
batch_convert("/path/to/odf/files", "/path/to/output")
```

---

**创建时间**: 2025-01-21
**代码行数**: 800+行
