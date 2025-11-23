# 办公自动化Schema转换体系

## 📑 目录

- [办公自动化Schema转换体系](#办公自动化schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
    - [1.1 转换目标](#11-转换目标)
  - [2. ODF到OOXML转换](#2-odf到ooxml转换)
    - [2.1 文档转换实现](#21-文档转换实现)
  - [3. OOXML到ODF转换](#3-ooxml到odf转换)
  - [4. 工作流管理实现](#4-工作流管理实现)
    - [4.1 BPMN工作流引擎](#41-bpmn工作流引擎)
    - [4.2 文档版本控制](#42-文档版本控制)
  - [5. 转换工具](#5-转换工具)
    - [5.1 LibreOffice集成](#51-libreoffice集成)
  - [6. 转换验证](#6-转换验证)
    - [6.1 文档转换验证](#61-文档转换验证)
  - [7. 办公自动化数据存储与分析](#7-办公自动化数据存储与分析)
    - [7.1 PostgreSQL OA数据存储](#71-postgresql-oa数据存储)
    - [7.2 OA数据分析查询](#72-oa数据分析查询)

---

## 1. 转换体系概述

办公自动化Schema转换体系支持ODF文档、OOXML文档、
数据库存储之间的转换。

### 1.1 转换目标

1. **ODF到OOXML转换**：ODF文档到OOXML文档
2. **OOXML到ODF转换**：OOXML文档到ODF文档
3. **数据到数据库转换**：办公自动化数据到PostgreSQL存储

---

## 2. ODF到OOXML转换

### 2.1 文档转换实现

**完整的ODF到OOXML转换实现**：

```python
import logging
import zipfile
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Any
from pathlib import Path
import tempfile
import shutil

logger = logging.getLogger(__name__)

class ODFToOOXMLConverter:
    """ODF到OOXML转换器"""

    # 文档类型映射
    DOCUMENT_TYPE_MAP = {
        "application/vnd.oasis.opendocument.text": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.oasis.opendocument.spreadsheet": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/vnd.oasis.opendocument.presentation": "application/vnd.openxmlformats-officedocument.presentationml.presentation"
    }

    # 文件扩展名映射
    EXTENSION_MAP = {
        ".odt": ".docx",
        ".ods": ".xlsx",
        ".odp": ".pptx"
    }

    def __init__(self):
        self.conversion_log = []

    def convert_document(self, odf_file_path: str, output_path: str = None) -> Optional[str]:
        """转换ODF文档到OOXML"""
        try:
            odf_path = Path(odf_file_path)

            if not odf_path.exists():
                raise FileNotFoundError(f"ODF file not found: {odf_file_path}")

            # 确定输出路径
            if output_path is None:
                output_path = str(odf_path.with_suffix(self._get_ooxml_extension(odf_path.suffix)))

            # 根据文档类型选择转换方法
            mime_type = self._detect_mime_type(odf_path)

            if "text" in mime_type:
                return self._convert_odt_to_docx(odf_path, output_path)
            elif "spreadsheet" in mime_type:
                return self._convert_ods_to_xlsx(odf_path, output_path)
            elif "presentation" in mime_type:
                return self._convert_odp_to_pptx(odf_path, output_path)
            else:
                raise ValueError(f"Unsupported ODF document type: {mime_type}")

        except Exception as e:
            logger.error(f"Failed to convert ODF document: {e}")
            return None

    def _convert_odt_to_docx(self, odf_path: Path, output_path: str) -> str:
        """转换ODT到DOCX"""
        # 创建临时目录
        with tempfile.TemporaryDirectory() as temp_dir:
            # 解压ODF文件
            odf_temp_dir = Path(temp_dir) / "odf"
            odf_temp_dir.mkdir()

            with zipfile.ZipFile(odf_path, 'r') as odf_zip:
                odf_zip.extractall(odf_temp_dir)

            # 读取ODF内容
            content_xml = odf_temp_dir / "content.xml"
            styles_xml = odf_temp_dir / "styles.xml"

            # 创建DOCX结构
            docx_temp_dir = Path(temp_dir) / "docx"
            docx_temp_dir.mkdir()

            # 创建DOCX目录结构
            (docx_temp_dir / "word").mkdir()
            (docx_temp_dir / "_rels").mkdir()
            (docx_temp_dir / "word" / "_rels").mkdir()

            # 转换内容
            self._convert_odt_content_to_docx(content_xml, styles_xml, docx_temp_dir)

            # 创建DOCX文件
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as docx_zip:
                self._package_docx(docx_temp_dir, docx_zip)

            logger.info(f"Converted ODT to DOCX: {output_path}")
            return output_path

    def _convert_ods_to_xlsx(self, odf_path: Path, output_path: str) -> str:
        """转换ODS到XLSX"""
        # 创建临时目录
        with tempfile.TemporaryDirectory() as temp_dir:
            # 解压ODF文件
            odf_temp_dir = Path(temp_dir) / "odf"
            odf_temp_dir.mkdir()

            with zipfile.ZipFile(odf_path, 'r') as odf_zip:
                odf_zip.extractall(odf_temp_dir)

            # 读取ODS内容
            content_xml = odf_temp_dir / "content.xml"
            styles_xml = odf_temp_dir / "styles.xml"

            # 创建XLSX结构
            xlsx_temp_dir = Path(temp_dir) / "xlsx"
            xlsx_temp_dir.mkdir()

            # 创建XLSX目录结构
            (xlsx_temp_dir / "xl").mkdir()
            (xlsx_temp_dir / "xl" / "worksheets").mkdir()
            (xlsx_temp_dir / "xl" / "_rels").mkdir()
            (xlsx_temp_dir / "_rels").mkdir()

            # 转换内容
            self._convert_ods_content_to_xlsx(content_xml, styles_xml, xlsx_temp_dir)

            # 创建XLSX文件
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as xlsx_zip:
                self._package_xlsx(xlsx_temp_dir, xlsx_zip)

            logger.info(f"Converted ODS to XLSX: {output_path}")
            return output_path

    def _convert_odp_to_pptx(self, odf_path: Path, output_path: str) -> str:
        """转换ODP到PPTX"""
        # 创建临时目录
        with tempfile.TemporaryDirectory() as temp_dir:
            # 解压ODF文件
            odf_temp_dir = Path(temp_dir) / "odf"
            odf_temp_dir.mkdir()

            with zipfile.ZipFile(odf_path, 'r') as odf_zip:
                odf_zip.extractall(odf_temp_dir)

            # 读取ODP内容
            content_xml = odf_temp_dir / "content.xml"
            styles_xml = odf_temp_dir / "styles.xml"

            # 创建PPTX结构
            pptx_temp_dir = Path(temp_dir) / "pptx"
            pptx_temp_dir.mkdir()

            # 创建PPTX目录结构
            (pptx_temp_dir / "ppt").mkdir()
            (pptx_temp_dir / "ppt" / "slides").mkdir()
            (pptx_temp_dir / "ppt" / "_rels").mkdir()
            (pptx_temp_dir / "_rels").mkdir()

            # 转换内容
            self._convert_odp_content_to_pptx(content_xml, styles_xml, pptx_temp_dir)

            # 创建PPTX文件
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as pptx_zip:
                self._package_pptx(pptx_temp_dir, pptx_zip)

            logger.info(f"Converted ODP to PPTX: {output_path}")
            return output_path

    def _convert_odt_content_to_docx(self, content_xml: Path, styles_xml: Path, docx_dir: Path):
        """转换ODT内容到DOCX"""
        # 读取ODF内容XML
        tree = ET.parse(content_xml)
        root = tree.getroot()

        # 定义命名空间
        namespaces = {
            'office': 'urn:oasis:names:tc:opendocument:xmlns:office:1.0',
            'text': 'urn:oasis:names:tc:opendocument:xmlns:text:1.0',
            'style': 'urn:oasis:names:tc:opendocument:xmlns:style:1.0'
        }

        # 创建DOCX document.xml
        docx_ns = {
            'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
        }

        document = ET.Element('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}document')
        document.set('xmlns:w', 'http://schemas.openxmlformats.org/wordprocessingml/2006/main')

        body = ET.SubElement(document, '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}body')

        # 转换段落
        text_elements = root.findall('.//{urn:oasis:names:tc:opendocument:xmlns:text:1.0}p', namespaces)
        for text_elem in text_elements:
            para = ET.SubElement(body, '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p')
            run = ET.SubElement(para, '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}r')
            text = ET.SubElement(run, '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t')
            text.text = text_elem.text or ""

        # 保存document.xml
        docx_doc_path = docx_dir / "word" / "document.xml"
        tree_docx = ET.ElementTree(document)
        tree_docx.write(docx_doc_path, encoding='utf-8', xml_declaration=True)

    def _convert_ods_content_to_xlsx(self, content_xml: Path, styles_xml: Path, xlsx_dir: Path):
        """转换ODS内容到XLSX"""
        # 读取ODS内容XML
        tree = ET.parse(content_xml)
        root = tree.getroot()

        # 定义命名空间
        namespaces = {
            'office': 'urn:oasis:names:tc:opendocument:xmlns:office:1.0',
            'table': 'urn:oasis:names:tc:opendocument:xmlns:table:1.0',
            'text': 'urn:oasis:names:tc:opendocument:xmlns:text:1.0'
        }

        # 查找所有表格
        spreadsheets = root.findall('.//{urn:oasis:names:tc:opendocument:xmlns:office:1.0}spreadsheet', namespaces)

        sheet_index = 1
        for spreadsheet in spreadsheets:
            tables = spreadsheet.findall('.//{urn:oasis:names:tc:opendocument:xmlns:table:1.0}table', namespaces)

            for table in tables:
                # 创建XLSX工作表
                self._create_xlsx_worksheet(table, xlsx_dir, sheet_index, namespaces)
                sheet_index += 1

    def _convert_odp_content_to_pptx(self, content_xml: Path, styles_xml: Path, pptx_dir: Path):
        """转换ODP内容到PPTX"""
        # 读取ODP内容XML
        tree = ET.parse(content_xml)
        root = tree.getroot()

        # 定义命名空间
        namespaces = {
            'office': 'urn:oasis:names:tc:opendocument:xmlns:office:1.0',
            'draw': 'urn:oasis:names:tc:opendocument:xmlns:drawing:1.0'
        }

        # 查找所有幻灯片
        presentations = root.findall('.//{urn:oasis:names:tc:opendocument:xmlns:office:1.0}presentation', namespaces)

        slide_index = 1
        for presentation in presentations:
            pages = presentation.findall('.//{urn:oasis:names:tc:opendocument:xmlns:drawing:1.0}page', namespaces)

            for page in pages:
                # 创建PPTX幻灯片
                self._create_pptx_slide(page, pptx_dir, slide_index, namespaces)
                slide_index += 1

    def _create_xlsx_worksheet(self, table, xlsx_dir: Path, sheet_index: int, namespaces: Dict):
        """创建XLSX工作表"""
        # 创建worksheet XML
        worksheet_ns = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'
        worksheet = ET.Element(f'{{{worksheet_ns}}}worksheet')
        worksheet.set('xmlns', worksheet_ns)

        sheetData = ET.SubElement(worksheet, f'{{{worksheet_ns}}}sheetData')

        # 转换表格行
        rows = table.findall('.//{urn:oasis:names:tc:opendocument:xmlns:table:1.0}table-row', namespaces)
        for row_idx, row in enumerate(rows, start=1):
            xlsx_row = ET.SubElement(sheetData, f'{{{worksheet_ns}}}row')
            xlsx_row.set('r', str(row_idx))

            cells = row.findall('.//{urn:oasis:names:tc:opendocument:xmlns:table:1.0}table-cell', namespaces)
            for col_idx, cell in enumerate(cells, start=1):
                xlsx_cell = ET.SubElement(xlsx_row, f'{{{worksheet_ns}}}c')
                xlsx_cell.set('r', f'{self._col_letter(col_idx)}{row_idx}')

                # 获取单元格值
                text_elem = cell.find('.//{urn:oasis:names:tc:opendocument:xmlns:text:1.0}p', namespaces)
                if text_elem is not None and text_elem.text:
                    v = ET.SubElement(xlsx_cell, f'{{{worksheet_ns}}}v')
                    v.text = text_elem.text

        # 保存worksheet
        worksheet_path = xlsx_dir / "xl" / "worksheets" / f"sheet{sheet_index}.xml"
        tree = ET.ElementTree(worksheet)
        tree.write(worksheet_path, encoding='utf-8', xml_declaration=True)

    def _create_pptx_slide(self, page, pptx_dir: Path, slide_index: int, namespaces: Dict):
        """创建PPTX幻灯片"""
        # 创建slide XML
        slide_ns = 'http://schemas.openxmlformats.org/presentationml/2006/main'
        slide = ET.Element(f'{{{slide_ns}}}sld')
        slide.set('xmlns:a', 'http://schemas.openxmlformats.org/drawingml/2006/main')
        slide.set('xmlns:r', 'http://schemas.openxmlformats.org/officeDocument/2006/relationships')
        slide.set('xmlns:p', slide_ns)

        cSld = ET.SubElement(slide, f'{{{slide_ns}}}cSld')
        spTree = ET.SubElement(cSld, f'{{{slide_ns}}}spTree')

        # 转换页面内容
        # 这里需要根据ODP的实际结构进行转换

        # 保存slide
        slide_path = pptx_dir / "ppt" / "slides" / f"slide{slide_index}.xml"
        tree = ET.ElementTree(slide)
        tree.write(slide_path, encoding='utf-8', xml_declaration=True)

    def _package_docx(self, docx_dir: Path, docx_zip: zipfile.ZipFile):
        """打包DOCX文件"""
        # 添加必要文件
        files_to_add = [
            ("[Content_Types].xml", "[Content_Types].xml"),
            ("_rels/.rels", "_rels/.rels"),
            ("word/document.xml", "word/document.xml"),
            ("word/_rels/document.xml.rels", "word/_rels/document.xml.rels")
        ]

        for file_path, zip_path in files_to_add:
            full_path = docx_dir / file_path
            if full_path.exists():
                docx_zip.write(full_path, zip_path)

    def _package_xlsx(self, xlsx_dir: Path, xlsx_zip: zipfile.ZipFile):
        """打包XLSX文件"""
        # 添加必要文件
        files_to_add = [
            ("[Content_Types].xml", "[Content_Types].xml"),
            ("_rels/.rels", "_rels/.rels"),
            ("xl/workbook.xml", "xl/workbook.xml"),
            ("xl/_rels/workbook.xml.rels", "xl/_rels/workbook.xml.rels")
        ]

        for file_path, zip_path in files_to_add:
            full_path = xlsx_dir / file_path
            if full_path.exists():
                xlsx_zip.write(full_path, zip_path)

        # 添加所有工作表
        worksheets_dir = xlsx_dir / "xl" / "worksheets"
        if worksheets_dir.exists():
            for worksheet_file in worksheets_dir.glob("*.xml"):
                rel_path = worksheet_file.relative_to(xlsx_dir)
                xlsx_zip.write(worksheet_file, str(rel_path))

    def _package_pptx(self, pptx_dir: Path, pptx_zip: zipfile.ZipFile):
        """打包PPTX文件"""
        # 添加必要文件
        files_to_add = [
            ("[Content_Types].xml", "[Content_Types].xml"),
            ("_rels/.rels", "_rels/.rels"),
            ("ppt/presentation.xml", "ppt/presentation.xml"),
            ("ppt/_rels/presentation.xml.rels", "ppt/_rels/presentation.xml.rels")
        ]

        for file_path, zip_path in files_to_add:
            full_path = pptx_dir / file_path
            if full_path.exists():
                pptx_zip.write(full_path, zip_path)

        # 添加所有幻灯片
        slides_dir = pptx_dir / "ppt" / "slides"
        if slides_dir.exists():
            for slide_file in slides_dir.glob("*.xml"):
                rel_path = slide_file.relative_to(pptx_dir)
                pptx_zip.write(slide_file, str(rel_path))

    def _detect_mime_type(self, file_path: Path) -> str:
        """检测MIME类型"""
        # 从文件扩展名判断
        ext = file_path.suffix.lower()
        mime_map = {
            '.odt': 'application/vnd.oasis.opendocument.text',
            '.ods': 'application/vnd.oasis.opendocument.spreadsheet',
            '.odp': 'application/vnd.oasis.opendocument.presentation'
        }
        return mime_map.get(ext, 'application/octet-stream')

    def _get_ooxml_extension(self, odf_extension: str) -> str:
        """获取OOXML扩展名"""
        return self.EXTENSION_MAP.get(odf_extension.lower(), '.docx')

    def _col_letter(self, col_num: int) -> str:
        """将列号转换为字母（1->A, 2->B, ...）"""
        result = ""
        while col_num > 0:
            col_num -= 1
            result = chr(65 + (col_num % 26)) + result
            col_num //= 26
        return result

    def convert_metadata(self, odf_file_path: str, ooxml_file_path: str):
        """转换文档元数据"""
        try:
            odf_path = Path(odf_file_path)
            ooxml_path = Path(ooxml_file_path)

            # 读取ODF元数据
            with zipfile.ZipFile(odf_path, 'r') as odf_zip:
                if 'meta.xml' in odf_zip.namelist():
                    meta_xml = odf_zip.read('meta.xml')
                    odf_meta = self._parse_odf_metadata(meta_xml)
                else:
                    odf_meta = {}

            # 转换元数据到OOXML格式
            ooxml_meta = self._convert_metadata_to_ooxml(odf_meta)

            # 更新OOXML文件的元数据
            self._update_ooxml_metadata(ooxml_path, ooxml_meta)

            logger.info(f"Converted metadata from ODF to OOXML")
        except Exception as e:
            logger.error(f"Failed to convert metadata: {e}")

    def _parse_odf_metadata(self, meta_xml: bytes) -> Dict:
        """解析ODF元数据"""
        tree = ET.fromstring(meta_xml)
        namespaces = {
            'office': 'urn:oasis:names:tc:opendocument:xmlns:office:1.0',
            'meta': 'urn:oasis:names:tc:opendocument:xmlns:meta:1.0',
            'dc': 'http://purl.org/dc/elements/1.1/'
        }

        metadata = {}

        # 标题
        title_elem = tree.find('.//{http://purl.org/dc/elements/1.1/}title', namespaces)
        if title_elem is not None:
            metadata['title'] = title_elem.text or ""

        # 作者
        creator_elem = tree.find('.//{http://purl.org/dc/elements/1.1/}creator', namespaces)
        if creator_elem is not None:
            metadata['creator'] = creator_elem.text or ""

        # 主题
        subject_elem = tree.find('.//{http://purl.org/dc/elements/1.1/}subject', namespaces)
        if subject_elem is not None:
            metadata['subject'] = subject_elem.text or ""

        # 关键词
        keywords_elem = tree.find('.//{urn:oasis:names:tc:opendocument:xmlns:meta:1.0}keyword', namespaces)
        if keywords_elem is not None:
            metadata['keywords'] = keywords_elem.text or ""

        # 描述
        description_elem = tree.find('.//{http://purl.org/dc/elements/1.1/}description', namespaces)
        if description_elem is not None:
            metadata['description'] = description_elem.text or ""

        # 创建时间
        creation_date_elem = tree.find('.//{urn:oasis:names:tc:opendocument:xmlns:meta:1.0}creation-date', namespaces)
        if creation_date_elem is not None:
            metadata['creation_date'] = creation_date_elem.text or ""

        # 修改时间
        modification_date_elem = tree.find('.//{urn:oasis:names:tc:opendocument:xmlns:meta:1.0}modification-date', namespaces)
        if modification_date_elem is not None:
            metadata['modification_date'] = modification_date_elem.text or ""

        return metadata

    def _convert_metadata_to_ooxml(self, odf_meta: Dict) -> Dict:
        """将ODF元数据转换为OOXML格式"""
        ooxml_meta = {}

        # 映射字段
        field_mapping = {
            'title': 'title',
            'creator': 'creator',
            'subject': 'subject',
            'keywords': 'keywords',
            'description': 'description',
            'creation_date': 'created',
            'modification_date': 'modified'
        }

        for odf_key, ooxml_key in field_mapping.items():
            if odf_key in odf_meta:
                ooxml_meta[ooxml_key] = odf_meta[odf_key]

        return ooxml_meta

    def _update_ooxml_metadata(self, ooxml_path: Path, metadata: Dict):
        """更新OOXML文件的元数据"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # 解压OOXML文件
            temp_ooxml_dir = Path(temp_dir) / "ooxml"
            temp_ooxml_dir.mkdir()

            with zipfile.ZipFile(ooxml_path, 'r') as ooxml_zip:
                ooxml_zip.extractall(temp_ooxml_dir)

            # 创建或更新core.xml（元数据文件）
            core_xml_path = temp_ooxml_dir / "docProps" / "core.xml"
            core_xml_path.parent.mkdir(exist_ok=True)

            self._create_core_xml(core_xml_path, metadata)

            # 重新打包OOXML文件
            with zipfile.ZipFile(ooxml_path, 'w', zipfile.ZIP_DEFLATED) as ooxml_zip:
                for file_path in temp_ooxml_dir.rglob('*'):
                    if file_path.is_file():
                        rel_path = file_path.relative_to(temp_ooxml_dir)
                        ooxml_zip.write(file_path, str(rel_path))

    def _create_core_xml(self, core_xml_path: Path, metadata: Dict):
        """创建OOXML core.xml元数据文件"""
        namespaces = {
            'cp': 'http://schemas.openxmlformats.org/package/2006/metadata/core-properties',
            'dc': 'http://purl.org/dc/elements/1.1/',
            'dcterms': 'http://purl.org/dc/terms/',
            'dcmitype': 'http://purl.org/dc/dcmitype/',
            'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
        }

        core_properties = ET.Element('{http://schemas.openxmlformats.org/package/2006/metadata/core-properties}coreProperties')
        core_properties.set('xmlns:cp', namespaces['cp'])
        core_properties.set('xmlns:dc', namespaces['dc'])
        core_properties.set('xmlns:dcterms', namespaces['dcterms'])
        core_properties.set('xmlns:dcmitype', namespaces['dcmitype'])
        core_properties.set('xmlns:xsi', namespaces['xsi'])

        # 添加元数据字段
        if 'title' in metadata:
            title = ET.SubElement(core_properties, f'{{{namespaces["dc"]}}}title')
            title.text = metadata['title']

        if 'creator' in metadata:
            creator = ET.SubElement(core_properties, f'{{{namespaces["dc"]}}}creator')
            creator.text = metadata['creator']

        if 'subject' in metadata:
            subject = ET.SubElement(core_properties, f'{{{namespaces["dc"]}}}subject')
            subject.text = metadata['subject']

        if 'description' in metadata:
            description = ET.SubElement(core_properties, f'{{{namespaces["dc"]}}}description')
            description.text = metadata['description']

        if 'keywords' in metadata:
            keywords = ET.SubElement(core_properties, f'{{{namespaces["cp"]}}}keywords')
            keywords.text = metadata['keywords']

        if 'created' in metadata:
            created = ET.SubElement(core_properties, f'{{{namespaces["dcterms"]}}}created')
            created.set('{http://www.w3.org/2001/XMLSchema-instance}type', 'dcterms:W3CDTF')
            created.text = metadata['created']

        if 'modified' in metadata:
            modified = ET.SubElement(core_properties, f'{{{namespaces["dcterms"]}}}modified')
            modified.set('{http://www.w3.org/2001/XMLSchema-instance}type', 'dcterms:W3CDTF')
            modified.text = metadata['modified']

        # 保存core.xml
        tree = ET.ElementTree(core_properties)
        tree.write(core_xml_path, encoding='utf-8', xml_declaration=True)

    def convert_styles(self, odf_file_path: str, ooxml_file_path: str):
        """转换文档样式"""
        try:
            odf_path = Path(odf_file_path)
            ooxml_path = Path(ooxml_file_path)

            # 读取ODF样式
            with zipfile.ZipFile(odf_path, 'r') as odf_zip:
                if 'styles.xml' in odf_zip.namelist():
                    styles_xml = odf_zip.read('styles.xml')
                    odf_styles = self._parse_odf_styles(styles_xml)
                else:
                    odf_styles = {}

            # 转换样式到OOXML格式
            ooxml_styles = self._convert_styles_to_ooxml(odf_styles)

            # 更新OOXML文件的样式
            self._update_ooxml_styles(ooxml_path, ooxml_styles)

            logger.info(f"Converted styles from ODF to OOXML")
        except Exception as e:
            logger.error(f"Failed to convert styles: {e}")

    def _parse_odf_styles(self, styles_xml: bytes) -> Dict:
        """解析ODF样式"""
        tree = ET.fromstring(styles_xml)
        namespaces = {
            'office': 'urn:oasis:names:tc:opendocument:xmlns:office:1.0',
            'style': 'urn:oasis:names:tc:opendocument:xmlns:style:1.0',
            'fo': 'urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0'
        }

        styles = {
            'paragraph_styles': {},
            'text_styles': {},
            'table_styles': {}
        }

        # 解析段落样式
        para_styles = tree.findall('.//{urn:oasis:names:tc:opendocument:xmlns:style:1.0}style[@style:family="paragraph"]', namespaces)
        for style in para_styles:
            style_name = style.get('{urn:oasis:names:tc:opendocument:xmlns:style:1.0}name', '')
            style_props = {}

            # 字体属性
            text_props = style.find('.//{urn:oasis:names:tc:opendocument:xmlns:style:1.0}text-properties', namespaces)
            if text_props is not None:
                if text_props.get('{urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0}font-size'):
                    style_props['font_size'] = text_props.get('{urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0}font-size')
                if text_props.get('{urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0}font-weight'):
                    style_props['font_weight'] = text_props.get('{urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0}font-weight')
                if text_props.get('{urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0}font-style'):
                    style_props['font_style'] = text_props.get('{urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0}font-style')
                if text_props.get('{urn:oasis:names:tc:opendocument:xmlns:style:1.0}font-name'):
                    style_props['font_name'] = text_props.get('{urn:oasis:names:tc:opendocument:xmlns:style:1.0}font-name')

            # 段落属性
            para_props = style.find('.//{urn:oasis:names:tc:opendocument:xmlns:style:1.0}paragraph-properties', namespaces)
            if para_props is not None:
                if para_props.get('{urn:oasis:names:tc:opendocument:xmlns:fo:1.0}text-align'):
                    style_props['text_align'] = para_props.get('{urn:oasis:names:tc:opendocument:xmlns:fo:1.0}text-align')
                if para_props.get('{urn:oasis:names:tc:opendocument:xmlns:fo:1.0}margin-left'):
                    style_props['margin_left'] = para_props.get('{urn:oasis:names:tc:opendocument:xmlns:fo:1.0}margin-left')
                if para_props.get('{urn:oasis:names:tc:opendocument:xmlns:fo:1.0}margin-right'):
                    style_props['margin_right'] = para_props.get('{urn:oasis:names:tc:opendocument:xmlns:fo:1.0}margin-right')

            styles['paragraph_styles'][style_name] = style_props

        return styles

    def _convert_styles_to_ooxml(self, odf_styles: Dict) -> Dict:
        """将ODF样式转换为OOXML格式"""
        ooxml_styles = {
            'paragraph_styles': {},
            'character_styles': {},
            'table_styles': {}
        }

        # 转换段落样式
        for style_name, style_props in odf_styles.get('paragraph_styles', {}).items():
            ooxml_style = {}

            # 字体属性映射
            if 'font_size' in style_props:
                ooxml_style['font_size'] = self._convert_font_size(style_props['font_size'])
            if 'font_weight' in style_props:
                ooxml_style['bold'] = style_props['font_weight'] == 'bold'
            if 'font_style' in style_props:
                ooxml_style['italic'] = style_props['font_style'] == 'italic'
            if 'font_name' in style_props:
                ooxml_style['font_name'] = style_props['font_name']

            # 段落属性映射
            if 'text_align' in style_props:
                ooxml_style['alignment'] = self._convert_alignment(style_props['text_align'])
            if 'margin_left' in style_props:
                ooxml_style['left_margin'] = self._convert_margin(style_props['margin_left'])
            if 'margin_right' in style_props:
                ooxml_style['right_margin'] = self._convert_margin(style_props['margin_right'])

            ooxml_styles['paragraph_styles'][style_name] = ooxml_style

        return ooxml_styles

    def _convert_font_size(self, odf_size: str) -> int:
        """转换字体大小（pt到half-points）"""
        try:
            # ODF使用pt，OOXML使用half-points
            pt_value = float(odf_size.replace('pt', '').strip())
            return int(pt_value * 2)
        except:
            return 24  # 默认12pt

    def _convert_alignment(self, odf_align: str) -> str:
        """转换对齐方式"""
        align_map = {
            'left': 'left',
            'right': 'right',
            'center': 'center',
            'justify': 'both'
        }
        return align_map.get(odf_align.lower(), 'left')

    def _convert_margin(self, odf_margin: str) -> int:
        """转换边距（cm到twips，1cm = 567 twips）"""
        try:
            cm_value = float(odf_margin.replace('cm', '').strip())
            return int(cm_value * 567)
        except:
            return 0

    def _update_ooxml_styles(self, ooxml_path: Path, styles: Dict):
        """更新OOXML文件的样式"""
        # 这里需要根据文档类型（DOCX/XLSX/PPTX）更新相应的样式文件
        # DOCX使用styles.xml，XLSX使用styles.xml，PPTX使用theme和slide master
        # 由于实现较复杂，这里提供基础框架
        logger.info(f"Updating OOXML styles: {len(styles.get('paragraph_styles', {}))} paragraph styles")
```

---

## 3. OOXML到ODF转换

**转换规则**：

- DOCX → ODT
- XLSX → ODS
- PPTX → ODP

**完整转换实现**：

```python
class OOXMLToODFConverter:
    """OOXML到ODF转换器"""

    # 文档类型映射
    DOCUMENT_TYPE_MAP = {
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "application/vnd.oasis.opendocument.text",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "application/vnd.oasis.opendocument.spreadsheet",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation": "application/vnd.oasis.opendocument.presentation"
    }

    # 文件扩展名映射
    EXTENSION_MAP = {
        ".docx": ".odt",
        ".xlsx": ".ods",
        ".pptx": ".odp"
    }

    def __init__(self):
        self.conversion_log = []

    def convert_document(self, ooxml_file_path: str, output_path: str = None) -> Optional[str]:
        """转换OOXML文档到ODF"""
        try:
            ooxml_path = Path(ooxml_file_path)

            if not ooxml_path.exists():
                raise FileNotFoundError(f"OOXML file not found: {ooxml_file_path}")

            # 确定输出路径
            if output_path is None:
                output_path = str(ooxml_path.with_suffix(self._get_odf_extension(ooxml_path.suffix)))

            # 根据文档类型选择转换方法
            mime_type = self._detect_mime_type(ooxml_path)

            if "wordprocessingml" in mime_type:
                return self._convert_docx_to_odt(ooxml_path, output_path)
            elif "spreadsheetml" in mime_type:
                return self._convert_xlsx_to_ods(ooxml_path, output_path)
            elif "presentationml" in mime_type:
                return self._convert_pptx_to_odp(ooxml_path, output_path)
            else:
                raise ValueError(f"Unsupported OOXML document type: {mime_type}")

        except Exception as e:
            logger.error(f"Failed to convert OOXML document: {e}")
            return None

    def _convert_docx_to_odt(self, ooxml_path: Path, output_path: str) -> str:
        """转换DOCX到ODT"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # 解压DOCX文件
            docx_temp_dir = Path(temp_dir) / "docx"
            docx_temp_dir.mkdir()

            with zipfile.ZipFile(ooxml_path, 'r') as docx_zip:
                docx_zip.extractall(docx_temp_dir)

            # 读取DOCX内容
            document_xml = docx_temp_dir / "word" / "document.xml"

            # 创建ODF结构
            odf_temp_dir = Path(temp_dir) / "odf"
            odf_temp_dir.mkdir()

            # 转换内容
            self._convert_docx_content_to_odt(document_xml, odf_temp_dir)

            # 创建ODF文件
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as odf_zip:
                self._package_odf(odf_temp_dir, odf_zip)

            logger.info(f"Converted DOCX to ODT: {output_path}")
            return output_path

    def _convert_xlsx_to_ods(self, ooxml_path: Path, output_path: str) -> str:
        """转换XLSX到ODS"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # 解压XLSX文件
            xlsx_temp_dir = Path(temp_dir) / "xlsx"
            xlsx_temp_dir.mkdir()

            with zipfile.ZipFile(ooxml_path, 'r') as xlsx_zip:
                xlsx_zip.extractall(xlsx_temp_dir)

            # 读取XLSX内容
            worksheets_dir = xlsx_temp_dir / "xl" / "worksheets"

            # 创建ODF结构
            odf_temp_dir = Path(temp_dir) / "odf"
            odf_temp_dir.mkdir()

            # 转换内容
            self._convert_xlsx_content_to_ods(worksheets_dir, odf_temp_dir)

            # 创建ODF文件
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as odf_zip:
                self._package_odf(odf_temp_dir, odf_zip)

            logger.info(f"Converted XLSX to ODS: {output_path}")
            return output_path

    def _convert_pptx_to_odp(self, ooxml_path: Path, output_path: str) -> str:
        """转换PPTX到ODP"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # 解压PPTX文件
            pptx_temp_dir = Path(temp_dir) / "pptx"
            pptx_temp_dir.mkdir()

            with zipfile.ZipFile(ooxml_path, 'r') as pptx_zip:
                pptx_zip.extractall(pptx_temp_dir)

            # 读取PPTX内容
            slides_dir = pptx_temp_dir / "ppt" / "slides"

            # 创建ODF结构
            odf_temp_dir = Path(temp_dir) / "odf"
            odf_temp_dir.mkdir()

            # 转换内容
            self._convert_pptx_content_to_odp(slides_dir, odf_temp_dir)

            # 创建ODF文件
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as odf_zip:
                self._package_odf(odf_temp_dir, odf_zip)

            logger.info(f"Converted PPTX to ODP: {output_path}")
            return output_path

    def _convert_docx_content_to_odt(self, document_xml: Path, odf_dir: Path):
        """转换DOCX内容到ODT"""
        # 读取DOCX内容XML
        tree = ET.parse(document_xml)
        root = tree.getroot()

        # 定义命名空间
        docx_ns = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'

        # 创建ODF content.xml
        odf_ns = {
            'office': 'urn:oasis:names:tc:opendocument:xmlns:office:1.0',
            'text': 'urn:oasis:names:tc:opendocument:xmlns:text:1.0'
        }

        office_document = ET.Element('{urn:oasis:names:tc:opendocument:xmlns:office:1.0}document-content')
        office_document.set('xmlns:office', 'urn:oasis:names:tc:opendocument:xmlns:office:1.0')
        office_document.set('xmlns:text', 'urn:oasis:names:tc:opendocument:xmlns:text:1.0')

        body = ET.SubElement(office_document, '{urn:oasis:names:tc:opendocument:xmlns:office:1.0}body')
        text = ET.SubElement(body, '{urn:oasis:names:tc:opendocument:xmlns:office:1.0}text')

        # 转换段落
        paragraphs = root.findall(f'.//{{{docx_ns}}}p')
        for para in paragraphs:
            p = ET.SubElement(text, '{urn:oasis:names:tc:opendocument:xmlns:text:1.0}p')

            # 转换文本运行
            runs = para.findall(f'.//{{{docx_ns}}}r')
            for run in runs:
                text_nodes = run.findall(f'.//{{{docx_ns}}}t')
                for text_node in text_nodes:
                    if text_node.text:
                        span = ET.SubElement(p, '{urn:oasis:names:tc:opendocument:xmlns:text:1.0}span')
                        span.text = text_node.text

        # 保存content.xml
        content_path = odf_dir / "content.xml"
        tree_odf = ET.ElementTree(office_document)
        tree_odf.write(content_path, encoding='utf-8', xml_declaration=True)

    def _convert_xlsx_content_to_ods(self, worksheets_dir: Path, odf_dir: Path):
        """转换XLSX内容到ODS"""
        # 创建ODF content.xml
        odf_ns = {
            'office': 'urn:oasis:names:tc:opendocument:xmlns:office:1.0',
            'table': 'urn:oasis:names:tc:opendocument:xmlns:table:1.0',
            'text': 'urn:oasis:names:tc:opendocument:xmlns:text:1.0'
        }

        office_document = ET.Element('{urn:oasis:names:tc:opendocument:xmlns:office:1.0}document-content')
        office_document.set('xmlns:office', 'urn:oasis:names:tc:opendocument:xmlns:office:1.0')
        office_document.set('xmlns:table', 'urn:oasis:names:tc:opendocument:xmlns:table:1.0')
        office_document.set('xmlns:text', 'urn:oasis:names:tc:opendocument:xmlns:text:1.0')

        body = ET.SubElement(office_document, '{urn:oasis:names:tc:opendocument:xmlns:office:1.0}body')
        spreadsheet = ET.SubElement(body, '{urn:oasis:names:tc:opendocument:xmlns:office:1.0}spreadsheet')

        # 转换所有工作表
        for worksheet_file in worksheets_dir.glob("*.xml"):
            self._convert_xlsx_worksheet_to_ods_table(worksheet_file, spreadsheet, odf_ns)

        # 保存content.xml
        content_path = odf_dir / "content.xml"
        tree_odf = ET.ElementTree(office_document)
        tree_odf.write(content_path, encoding='utf-8', xml_declaration=True)

    def _convert_xlsx_worksheet_to_ods_table(self, worksheet_file: Path, spreadsheet, odf_ns: Dict):
        """转换XLSX工作表到ODS表格"""
        tree = ET.parse(worksheet_file)
        root = tree.getroot()

        xlsx_ns = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'

        # 创建ODS表格
        table = ET.SubElement(spreadsheet, '{urn:oasis:names:tc:opendocument:xmlns:table:1.0}table')
        table.set('{urn:oasis:names:tc:opendocument:xmlns:table:1.0}name', worksheet_file.stem)

        # 转换行
        sheetData = root.find(f'.//{{{xlsx_ns}}}sheetData')
        if sheetData is not None:
            rows = sheetData.findall(f'.//{{{xlsx_ns}}}row')
            for row in rows:
                table_row = ET.SubElement(table, '{urn:oasis:names:tc:opendocument:xmlns:table:1.0}table-row')

                # 转换单元格
                cells = row.findall(f'.//{{{xlsx_ns}}}c')
                for cell in cells:
                    table_cell = ET.SubElement(table_row, '{urn:oasis:names:tc:opendocument:xmlns:table:1.0}table-cell')

                    # 获取单元格值
                    v = cell.find(f'.//{{{xlsx_ns}}}v')
                    if v is not None and v.text:
                        p = ET.SubElement(table_cell, '{urn:oasis:names:tc:opendocument:xmlns:text:1.0}p')
                        p.text = v.text

    def _convert_pptx_content_to_odp(self, slides_dir: Path, odf_dir: Path):
        """转换PPTX内容到ODP"""
        # 创建ODF content.xml
        odf_ns = {
            'office': 'urn:oasis:names:tc:opendocument:xmlns:office:1.0',
            'draw': 'urn:oasis:names:tc:opendocument:xmlns:drawing:1.0'
        }

        office_document = ET.Element('{urn:oasis:names:tc:opendocument:xmlns:office:1.0}document-content')
        office_document.set('xmlns:office', 'urn:oasis:names:tc:opendocument:xmlns:office:1.0')
        office_document.set('xmlns:draw', 'urn:oasis:names:tc:opendocument:xmlns:drawing:1.0')

        body = ET.SubElement(office_document, '{urn:oasis:names:tc:opendocument:xmlns:office:1.0}body')
        presentation = ET.SubElement(body, '{urn:oasis:names:tc:opendocument:xmlns:office:1.0}presentation')

        # 转换所有幻灯片
        for slide_file in sorted(slides_dir.glob("*.xml")):
            self._convert_pptx_slide_to_odp_page(slide_file, presentation, odf_ns)

        # 保存content.xml
        content_path = odf_dir / "content.xml"
        tree_odf = ET.ElementTree(office_document)
        tree_odf.write(content_path, encoding='utf-8', xml_declaration=True)

    def _convert_pptx_slide_to_odp_page(self, slide_file: Path, presentation, odf_ns: Dict):
        """转换PPTX幻灯片到ODP页面"""
        tree = ET.parse(slide_file)
        root = tree.getroot()

        # 创建ODP页面
        page = ET.SubElement(presentation, '{urn:oasis:names:tc:opendocument:xmlns:drawing:1.0}page')
        page.set('{urn:oasis:names:tc:opendocument:xmlns:drawing:1.0}name', slide_file.stem)

        # 转换幻灯片内容
        # 这里需要根据PPTX的实际结构进行转换

    def _package_odf(self, odf_dir: Path, odf_zip: zipfile.ZipFile):
        """打包ODF文件"""
        # 添加必要文件
        files_to_add = [
            "mimetype",
            "content.xml",
            "styles.xml",
            "meta.xml",
            "META-INF/manifest.xml"
        ]

        for file_name in files_to_add:
            file_path = odf_dir / file_name
            if file_path.exists():
                odf_zip.write(file_path, file_name)

    def _detect_mime_type(self, file_path: Path) -> str:
        """检测MIME类型"""
        ext = file_path.suffix.lower()
        mime_map = {
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
        }
        return mime_map.get(ext, 'application/octet-stream')

    def _get_odf_extension(self, ooxml_extension: str) -> str:
        """获取ODF扩展名"""
        return self.EXTENSION_MAP.get(ooxml_extension.lower(), '.odt')
```

---

## 4. 工作流管理实现

### 4.1 BPMN工作流引擎

**完整的工作流管理实现**：

```python
import logging
from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class ProcessStatus(Enum):
    """流程状态"""
    DRAFT = "Draft"
    SUBMITTED = "Submitted"
    IN_PROGRESS = "InProgress"
    APPROVED = "Approved"
    REJECTED = "Rejected"
    CANCELLED = "Cancelled"
    COMPLETED = "Completed"

class NodeType(Enum):
    """节点类型"""
    START = "Start"
    APPROVAL = "Approval"
    TASK = "Task"
    GATEWAY = "Gateway"
    END = "End"

class WorkflowEngine:
    """工作流引擎"""

    def __init__(self, storage):
        self.storage = storage
        self.process_definitions: Dict[str, Dict] = {}
        self.running_processes: Dict[str, Dict] = {}

    def define_process(self, process_id: str, process_definition: Dict):
        """定义工作流流程"""
        self.process_definitions[process_id] = process_definition
        logger.info(f"Defined process: {process_id}")

    def start_process(self, process_id: str, submitter: str, process_data: Dict) -> str:
        """启动流程实例"""
        if process_id not in self.process_definitions:
            raise ValueError(f"Process definition not found: {process_id}")

        definition = self.process_definitions[process_id]
        instance_id = f"{process_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"

        # 创建流程实例
        process_instance = {
            "instance_id": instance_id,
            "process_id": process_id,
            "process_name": definition.get("process_name"),
            "process_type": definition.get("process_type"),
            "submitter": submitter,
            "current_status": ProcessStatus.SUBMITTED.value,
            "current_node": self._get_start_node(definition),
            "process_data": process_data,
            "submit_time": datetime.now(),
            "nodes_history": []
        }

        self.running_processes[instance_id] = process_instance

        # 存储到数据库
        self.storage.store_process_approval({
            "process_id": instance_id,
            "process_name": definition.get("process_name"),
            "process_type": definition.get("process_type"),
            "submitter": submitter,
            "current_status": ProcessStatus.SUBMITTED.value,
            "submit_time": process_instance["submit_time"],
            "process_data": process_data
        })

        # 推进到第一个节点
        self._advance_process(instance_id)

        logger.info(f"Started process instance: {instance_id}")
        return instance_id

    def approve_node(self, instance_id: str, approver: str, approval_result: str, comment: str = ""):
        """审批节点"""
        if instance_id not in self.running_processes:
            raise ValueError(f"Process instance not found: {instance_id}")

        process = self.running_processes[instance_id]
        current_node_id = process["current_node"]

        # 记录审批
        self.storage.store_approval_record({
            "process_id": instance_id,
            "node_id": current_node_id,
            "approver": approver,
            "approval_result": approval_result,
            "approval_comment": comment,
            "approval_time": datetime.now()
        })

        # 更新节点历史
        process["nodes_history"].append({
            "node_id": current_node_id,
            "approver": approver,
            "result": approval_result,
            "time": datetime.now().isoformat()
        })

        if approval_result == "Approved":
            # 推进到下一个节点
            self._advance_process(instance_id)
        elif approval_result == "Rejected":
            # 流程被拒绝
            process["current_status"] = ProcessStatus.REJECTED.value
            process["complete_time"] = datetime.now()

            # 更新数据库
            self.storage.update_process_status(instance_id, ProcessStatus.REJECTED.value)

        logger.info(f"Node approved: {instance_id}, node: {current_node_id}, result: {approval_result}")

    def _advance_process(self, instance_id: str):
        """推进流程到下一个节点"""
        process = self.running_processes[instance_id]
        definition = self.process_definitions[process["process_id"]]

        current_node_id = process["current_node"]
        current_node = self._get_node_by_id(definition, current_node_id)

        if not current_node:
            return

        # 获取下一个节点
        next_node = self._get_next_node(definition, current_node)

        if next_node:
            if next_node["node_type"] == NodeType.END.value:
                # 流程完成
                process["current_status"] = ProcessStatus.COMPLETED.value
                process["complete_time"] = datetime.now()
                self.storage.update_process_status(instance_id, ProcessStatus.COMPLETED.value)
            else:
                # 移动到下一个节点
                process["current_node"] = next_node["node_id"]
                process["current_status"] = ProcessStatus.IN_PROGRESS.value
                self.storage.update_process_status(instance_id, ProcessStatus.IN_PROGRESS.value)
        else:
            # 没有下一个节点，流程完成
            process["current_status"] = ProcessStatus.COMPLETED.value
            process["complete_time"] = datetime.now()
            self.storage.update_process_status(instance_id, ProcessStatus.COMPLETED.value)

    def _get_start_node(self, definition: Dict) -> str:
        """获取开始节点"""
        nodes = definition.get("process_definition", {}).get("process_nodes", [])
        for node in nodes:
            if node.get("node_type") == NodeType.START.value:
                return node["node_id"]
        return nodes[0]["node_id"] if nodes else ""

    def _get_node_by_id(self, definition: Dict, node_id: str) -> Optional[Dict]:
        """根据ID获取节点"""
        nodes = definition.get("process_definition", {}).get("process_nodes", [])
        for node in nodes:
            if node.get("node_id") == node_id:
                return node
        return None

    def _get_next_node(self, definition: Dict, current_node: Dict) -> Optional[Dict]:
        """获取下一个节点"""
        nodes = definition.get("process_definition", {}).get("process_nodes", [])
        current_order = current_node.get("node_order", 0)

        for node in nodes:
            if node.get("node_order") == current_order + 1:
                return node

        return None

    def get_process_status(self, instance_id: str) -> Optional[Dict]:
        """获取流程状态"""
        return self.running_processes.get(instance_id)

    def assign_task(self, instance_id: str, node_id: str, assignee: str):
        """分配任务"""
        if instance_id not in self.running_processes:
            raise ValueError(f"Process instance not found: {instance_id}")

        process = self.running_processes[instance_id]
        definition = self.process_definitions[process["process_id"]]
        node = self._get_node_by_id(definition, node_id)

        if not node:
            raise ValueError(f"Node not found: {node_id}")

        # 存储任务分配
        self.storage.store_task_assignment({
            "process_id": instance_id,
            "node_id": node_id,
            "assignee": assignee,
            "assigned_time": datetime.now(),
            "task_status": "Assigned"
        })

        logger.info(f"Assigned task {node_id} to {assignee} in process {instance_id}")

    def get_process_statistics(self, process_id: str = None,
                              start_date: datetime = None,
                              end_date: datetime = None) -> Dict:
        """获取流程统计信息"""
        stats = {
            "total_processes": 0,
            "completed_processes": 0,
            "in_progress_processes": 0,
            "rejected_processes": 0,
            "average_duration_hours": 0.0,
            "node_statistics": {}
        }

        processes_to_analyze = []
        if process_id:
            processes_to_analyze = [
                p for p in self.running_processes.values()
                if p["process_id"] == process_id
            ]
        else:
            processes_to_analyze = list(self.running_processes.values())

        # 过滤日期范围
        if start_date or end_date:
            filtered_processes = []
            for p in processes_to_analyze:
                submit_time = p.get("submit_time")
                if submit_time:
                    if start_date and submit_time < start_date:
                        continue
                    if end_date and submit_time > end_date:
                        continue
                    filtered_processes.append(p)
            processes_to_analyze = filtered_processes

        stats["total_processes"] = len(processes_to_analyze)

        durations = []
        for process in processes_to_analyze:
            status = process.get("current_status")
            if status == ProcessStatus.COMPLETED.value:
                stats["completed_processes"] += 1
                if "submit_time" in process and "complete_time" in process:
                    duration = (process["complete_time"] - process["submit_time"]).total_seconds() / 3600
                    durations.append(duration)
            elif status == ProcessStatus.IN_PROGRESS.value:
                stats["in_progress_processes"] += 1
            elif status == ProcessStatus.REJECTED.value:
                stats["rejected_processes"] += 1

        if durations:
            stats["average_duration_hours"] = sum(durations) / len(durations)

        return stats

class BPMNParser:
    """BPMN流程解析器"""

    def __init__(self):
        self.namespaces = {
            'bpmn': 'http://www.omg.org/spec/BPMN/20100524/MODEL',
            'bpmndi': 'http://www.omg.org/spec/BPMN/20100524/DI',
            'dc': 'http://www.omg.org/spec/DD/20100524/DC',
            'di': 'http://www.omg.org/spec/DD/20100524/DI'
        }

    def parse_bpmn_file(self, bpmn_file_path: str) -> Dict:
        """解析BPMN文件"""
        tree = ET.parse(bpmn_file_path)
        root = tree.getroot()

        process_definition = {
            "process_id": root.get('id', ''),
            "process_name": root.get('name', ''),
            "nodes": [],
            "flows": [],
            "gateways": []
        }

        # 解析流程节点
        process_elem = root.find('.//{http://www.omg.org/spec/BPMN/20100524/MODEL}process', self.namespaces)
        if process_elem is not None:
            # 解析开始事件
            start_events = process_elem.findall('.//{http://www.omg.org/spec/BPMN/20100524/MODEL}startEvent', self.namespaces)
            for event in start_events:
                process_definition["nodes"].append({
                    "node_id": event.get('id', ''),
                    "node_name": event.get('name', ''),
                    "node_type": "Start"
                })

            # 解析任务节点
            tasks = process_elem.findall('.//{http://www.omg.org/spec/BPMN/20100524/MODEL}task', self.namespaces)
            for task in tasks:
                process_definition["nodes"].append({
                    "node_id": task.get('id', ''),
                    "node_name": task.get('name', ''),
                    "node_type": "Task",
                    "assignee": self._extract_assignee(task)
                })

            # 解析用户任务
            user_tasks = process_elem.findall('.//{http://www.omg.org/spec/BPMN/20100524/MODEL}userTask', self.namespaces)
            for task in user_tasks:
                process_definition["nodes"].append({
                    "node_id": task.get('id', ''),
                    "node_name": task.get('name', ''),
                    "node_type": "Approval",
                    "assignee": self._extract_assignee(task)
                })

            # 解析网关
            gateways = process_elem.findall('.//{http://www.omg.org/spec/BPMN/20100524/MODEL}exclusiveGateway', self.namespaces)
            for gateway in gateways:
                process_definition["gateways"].append({
                    "gateway_id": gateway.get('id', ''),
                    "gateway_name": gateway.get('name', ''),
                    "gateway_type": "Exclusive"
                })

            # 解析结束事件
            end_events = process_elem.findall('.//{http://www.omg.org/spec/BPMN/20100524/MODEL}endEvent', self.namespaces)
            for event in end_events:
                process_definition["nodes"].append({
                    "node_id": event.get('id', ''),
                    "node_name": event.get('name', ''),
                    "node_type": "End"
                })

            # 解析流程流
            flows = process_elem.findall('.//{http://www.omg.org/spec/BPMN/20100524/MODEL}sequenceFlow', self.namespaces)
            for flow in flows:
                process_definition["flows"].append({
                    "flow_id": flow.get('id', ''),
                    "source_ref": flow.get('sourceRef', ''),
                    "target_ref": flow.get('targetRef', ''),
                    "condition": self._extract_condition(flow)
                })

        return process_definition

    def _extract_assignee(self, task_elem) -> Optional[str]:
        """提取任务分配者"""
        # 查找humanPerformer或potentialOwner
        human_performer = task_elem.find('.//{http://www.omg.org/spec/BPMN/20100524/MODEL}humanPerformer', self.namespaces)
        if human_performer is not None:
            resource = human_performer.find('.//{http://www.omg.org/spec/BPMN/20100524/MODEL}resource', self.namespaces)
            if resource is not None:
                return resource.get('name', '')

        potential_owner = task_elem.find('.//{http://www.omg.org/spec/BPMN/20100524/MODEL}potentialOwner', self.namespaces)
        if potential_owner is not None:
            resource = potential_owner.find('.//{http://www.omg.org/spec/BPMN/20100524/MODEL}resource', self.namespaces)
            if resource is not None:
                return resource.get('name', '')

        return None

    def _extract_condition(self, flow_elem) -> Optional[str]:
        """提取流程条件"""
        condition = flow_elem.find('.//{http://www.omg.org/spec/BPMN/20100524/MODEL}conditionExpression', self.namespaces)
        if condition is not None:
            return condition.text
        return None

    def convert_to_workflow_definition(self, bpmn_definition: Dict) -> Dict:
        """将BPMN定义转换为工作流引擎定义"""
        workflow_def = {
            "process_id": bpmn_definition["process_id"],
            "process_name": bpmn_definition["process_name"],
            "process_type": "BPMN",
            "process_definition": {
                "process_nodes": []
            }
        }

        # 转换节点
        node_order = 1
        for node in bpmn_definition["nodes"]:
            workflow_node = {
                "node_id": node["node_id"],
                "node_name": node["node_name"],
                "node_type": node["node_type"],
                "node_order": node_order
            }

            if "assignee" in node:
                workflow_node["assignee"] = node["assignee"]

            workflow_def["process_definition"]["process_nodes"].append(workflow_node)
            node_order += 1

        # 添加网关信息
        if bpmn_definition["gateways"]:
            workflow_def["process_definition"]["gateways"] = bpmn_definition["gateways"]

        # 添加流程流信息
        if bpmn_definition["flows"]:
            workflow_def["process_definition"]["flows"] = bpmn_definition["flows"]

        return workflow_def

class ProcessMonitor:
    """流程监控器"""

    def __init__(self, workflow_engine: WorkflowEngine, storage):
        self.workflow_engine = workflow_engine
        self.storage = storage

    def monitor_process(self, instance_id: str) -> Dict:
        """监控流程实例"""
        process = self.workflow_engine.get_process_status(instance_id)
        if not process:
            return {}

        monitor_data = {
            "instance_id": instance_id,
            "process_id": process["process_id"],
            "current_status": process["current_status"],
            "current_node": process["current_node"],
            "submitter": process["submitter"],
            "submit_time": process["submit_time"].isoformat() if "submit_time" in process else None,
            "duration_hours": None,
            "node_history": process.get("nodes_history", []),
            "pending_tasks": [],
            "completed_tasks": []
        }

        # 计算持续时间
        if "submit_time" in process:
            if "complete_time" in process:
                duration = (process["complete_time"] - process["submit_time"]).total_seconds() / 3600
            else:
                duration = (datetime.now() - process["submit_time"]).total_seconds() / 3600
            monitor_data["duration_hours"] = round(duration, 2)

        # 获取待处理任务
        pending_tasks = self.storage.get_pending_tasks(instance_id)
        monitor_data["pending_tasks"] = pending_tasks

        # 获取已完成任务
        completed_tasks = self.storage.get_completed_tasks(instance_id)
        monitor_data["completed_tasks"] = completed_tasks

        return monitor_data

    def get_process_performance_metrics(self, process_id: str,
                                        start_date: datetime = None,
                                        end_date: datetime = None) -> Dict:
        """获取流程性能指标"""
        stats = self.workflow_engine.get_process_statistics(
            process_id, start_date, end_date
        )

        metrics = {
            "total_processes": stats["total_processes"],
            "completion_rate": 0.0,
            "rejection_rate": 0.0,
            "average_duration_hours": stats["average_duration_hours"],
            "throughput_per_day": 0.0
        }

        if stats["total_processes"] > 0:
            metrics["completion_rate"] = stats["completed_processes"] / stats["total_processes"]
            metrics["rejection_rate"] = stats["rejected_processes"] / stats["total_processes"]

        # 计算吞吐量
        if start_date and end_date:
            days = (end_date - start_date).days
            if days > 0:
                metrics["throughput_per_day"] = stats["total_processes"] / days

        return metrics
```

### 4.2 文档版本控制

**文档版本控制实现**：

```python
class DocumentVersionManager:
    """文档版本管理器"""

    def __init__(self, storage):
        self.storage = storage

    def create_version(self, document_id: str, author: str,
                      file_path: str, comment: str = "") -> int:
        """创建文档版本"""
        # 获取当前版本号
        current_version = self.storage.get_current_version(document_id)
        new_version = current_version + 1

        # 存储版本信息
        version_id = self.storage.store_document_version({
            "document_id": document_id,
            "version_number": new_version,
            "version_author": author,
            "version_comment": comment,
            "version_file_path": file_path
        })

        # 更新文档当前版本
        self.storage.update_document_version(document_id, new_version)

        logger.info(f"Created version {new_version} for document {document_id}")
        return new_version

    def get_version_history(self, document_id: str) -> List[Dict]:
        """获取版本历史"""
        return self.storage.get_document_versions(document_id)

    def restore_version(self, document_id: str, version_number: int) -> bool:
        """恢复指定版本"""
        version = self.storage.get_document_version(document_id, version_number)
        if not version:
            return False

        # 创建新版本（恢复的版本）
        current_version = self.storage.get_current_version(document_id)
        new_version = current_version + 1

        self.storage.store_document_version({
            "document_id": document_id,
            "version_number": new_version,
            "version_author": version["version_author"],
            "version_comment": f"Restored from version {version_number}",
            "version_file_path": version["version_file_path"]
        })

        self.storage.update_document_version(document_id, new_version)

        logger.info(f"Restored version {version_number} for document {document_id}")
        return True
```

---

## 5. 转换工具

### 5.1 LibreOffice集成

**LibreOffice命令行转换**：

```python
import subprocess
import logging

logger = logging.getLogger(__name__)

class LibreOfficeConverter:
    """LibreOffice转换器"""

    def __init__(self, libreoffice_path: str = "libreoffice"):
        self.libreoffice_path = libreoffice_path

    def convert_to_pdf(self, input_file: str, output_dir: str = None) -> bool:
        """转换为PDF"""
        cmd = [
            self.libreoffice_path,
            "--headless",
            "--convert-to", "pdf",
            "--outdir", output_dir or ".",
            input_file
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Failed to convert to PDF: {e}")
            return False

    def convert_odf_to_ooxml(self, input_file: str, output_dir: str = None) -> bool:
        """转换ODF到OOXML"""
        # 检测输入文件类型
        if input_file.endswith('.odt'):
            output_format = 'docx'
        elif input_file.endswith('.ods'):
            output_format = 'xlsx'
        elif input_file.endswith('.odp'):
            output_format = 'pptx'
        else:
            return False

        cmd = [
            self.libreoffice_path,
            "--headless",
            "--convert-to", output_format,
            "--outdir", output_dir or ".",
            input_file
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Failed to convert ODF to OOXML: {e}")
            return False
```

---

## 6. 转换验证

### 6.1 文档转换验证

**转换验证器实现**：

```python
class DocumentConversionValidator:
    """文档转换验证器"""

    def validate_odf_to_ooxml(self, odf_file: str, ooxml_file: str) -> bool:
        """验证ODF到OOXML转换"""
        # 检查文件是否存在
        if not Path(odf_file).exists() or not Path(ooxml_file).exists():
            return False

        # 检查文件大小（OOXML通常比ODF大）
        odf_size = Path(odf_file).stat().st_size
        ooxml_size = Path(ooxml_file).stat().st_size

        if ooxml_size == 0:
            return False

        # 检查文件格式
        if not self._is_valid_ooxml(ooxml_file):
            return False

        return True

    def validate_ooxml_to_odf(self, ooxml_file: str, odf_file: str) -> bool:
        """验证OOXML到ODF转换"""
        # 检查文件是否存在
        if not Path(ooxml_file).exists() or not Path(odf_file).exists():
            return False

        # 检查文件大小
        ooxml_size = Path(ooxml_file).stat().st_size
        odf_size = Path(odf_file).stat().st_size

        if odf_size == 0:
            return False

        # 检查文件格式
        if not self._is_valid_odf(odf_file):
            return False

        return True

    def _is_valid_ooxml(self, file_path: str) -> bool:
        """检查是否为有效的OOXML文件"""
        try:
            with zipfile.ZipFile(file_path, 'r') as zip_file:
                # 检查必要文件
                required_files = ['[Content_Types].xml', '_rels/.rels']
                for req_file in required_files:
                    if req_file not in zip_file.namelist():
                        return False
                return True
        except Exception:
            return False

    def _is_valid_odf(self, file_path: str) -> bool:
        """检查是否为有效的ODF文件"""
        try:
            with zipfile.ZipFile(file_path, 'r') as zip_file:
                # 检查必要文件
                required_files = ['mimetype', 'content.xml', 'META-INF/manifest.xml']
                for req_file in required_files:
                    if req_file not in zip_file.namelist():
                        return False
                return True
        except Exception:
            return False
```

---

## 7. 办公自动化数据存储与分析

### 7.1 PostgreSQL OA数据存储

**OA数据存储方案**：

```python
import psycopg2
import json
from typing import Dict, List, Optional
from datetime import datetime

class OAStorage:
    """办公自动化数据存储系统"""

    def __init__(self, connection_string: str):
        self.conn = psycopg2.connect(connection_string)
        self.cur = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        """创建OA数据表"""
        # 文档表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id BIGSERIAL PRIMARY KEY,
                document_id VARCHAR(20) UNIQUE NOT NULL,
                document_title VARCHAR(200) NOT NULL,
                document_type VARCHAR(50) NOT NULL,
                author VARCHAR(100) NOT NULL,
                file_path VARCHAR(500) NOT NULL,
                file_size BIGINT,
                mime_type VARCHAR(100),
                current_version INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 文档版本表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS document_versions (
                id BIGSERIAL PRIMARY KEY,
                document_id VARCHAR(20) NOT NULL,
                version_number INTEGER NOT NULL,
                version_author VARCHAR(100) NOT NULL,
                version_comment VARCHAR(500),
                version_file_path VARCHAR(500) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (document_id) REFERENCES documents(document_id),
                UNIQUE(document_id, version_number)
            )
        """)

        # 流程审批表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS process_approvals (
                id BIGSERIAL PRIMARY KEY,
                process_id VARCHAR(20) UNIQUE NOT NULL,
                process_name VARCHAR(200) NOT NULL,
                process_type VARCHAR(50) NOT NULL,
                submitter VARCHAR(100) NOT NULL,
                current_status VARCHAR(20) NOT NULL,
                current_node VARCHAR(10),
                submit_time TIMESTAMP NOT NULL,
                complete_time TIMESTAMP,
                process_data JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 审批记录表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS approval_records (
                id BIGSERIAL PRIMARY KEY,
                process_id VARCHAR(20) NOT NULL,
                node_id VARCHAR(10) NOT NULL,
                approver VARCHAR(100) NOT NULL,
                approval_result VARCHAR(20) NOT NULL,
                approval_comment VARCHAR(1000),
                approval_time TIMESTAMP NOT NULL,
                FOREIGN KEY (process_id) REFERENCES process_approvals(process_id)
            )
        """)

        # 任务表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id BIGSERIAL PRIMARY KEY,
                task_id VARCHAR(20) UNIQUE NOT NULL,
                task_title VARCHAR(200) NOT NULL,
                task_description TEXT,
                assignee VARCHAR(100) NOT NULL,
                assigner VARCHAR(100) NOT NULL,
                task_status VARCHAR(20) DEFAULT 'Todo',
                priority VARCHAR(20) DEFAULT 'Medium',
                due_date TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 文档内容表（全文索引）
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS document_contents (
                id BIGSERIAL PRIMARY KEY,
                document_id VARCHAR(20) NOT NULL,
                version_number INTEGER NOT NULL,
                content_text TEXT,
                content_html TEXT,
                content_json JSONB,
                extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (document_id) REFERENCES documents(document_id),
                UNIQUE(document_id, version_number)
            )
        """)

        # 创建全文索引
        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_document_contents_fulltext
            ON document_contents USING gin(to_tsvector('english', content_text))
        """)

        # 任务分配表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS task_assignments (
                id BIGSERIAL PRIMARY KEY,
                process_id VARCHAR(20) NOT NULL,
                node_id VARCHAR(10) NOT NULL,
                assignee VARCHAR(100) NOT NULL,
                assigned_time TIMESTAMP NOT NULL,
                task_status VARCHAR(20) DEFAULT 'Assigned',
                completed_time TIMESTAMP,
                FOREIGN KEY (process_id) REFERENCES process_approvals(process_id)
            )
        """)

        # 协作记录表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS collaboration_records (
                id BIGSERIAL PRIMARY KEY,
                document_id VARCHAR(20) NOT NULL,
                user_id VARCHAR(100) NOT NULL,
                action_type VARCHAR(50) NOT NULL,
                action_description TEXT,
                action_data JSONB,
                action_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (document_id) REFERENCES documents(document_id)
            )
        """)

        # 文档权限表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS document_permissions (
                id BIGSERIAL PRIMARY KEY,
                document_id VARCHAR(20) NOT NULL,
                user_id VARCHAR(100) NOT NULL,
                permission_type VARCHAR(20) NOT NULL,
                granted_by VARCHAR(100),
                granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (document_id) REFERENCES documents(document_id),
                UNIQUE(document_id, user_id, permission_type)
            )
        """)

        # 流程实例扩展表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS process_instances (
                id BIGSERIAL PRIMARY KEY,
                instance_id VARCHAR(50) UNIQUE NOT NULL,
                process_id VARCHAR(20) NOT NULL,
                process_name VARCHAR(200) NOT NULL,
                submitter VARCHAR(100) NOT NULL,
                current_status VARCHAR(20) NOT NULL,
                current_node VARCHAR(10),
                submit_time TIMESTAMP NOT NULL,
                complete_time TIMESTAMP,
                duration_hours NUMERIC(10, 2),
                process_data JSONB,
                nodes_history JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 创建索引
        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_documents_document_id
            ON documents(document_id)
        """)

        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_documents_author
            ON documents(author)
        """)

        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_documents_created_at
            ON documents(created_at DESC)
        """)

        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_document_versions_document_id
            ON document_versions(document_id, version_number DESC)
        """)

        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_document_contents_document_id
            ON document_contents(document_id, version_number)
        """)

        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_process_approvals_process_id
            ON process_approvals(process_id)
        """)

        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_process_approvals_status
            ON process_approvals(current_status, submit_time DESC)
        """)

        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_process_instances_instance_id
            ON process_instances(instance_id)
        """)

        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_process_instances_status
            ON process_instances(current_status, submit_time DESC)
        """)

        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_approval_records_process_id
            ON approval_records(process_id, approval_time DESC)
        """)

        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_task_assignments_process_id
            ON task_assignments(process_id, assigned_time DESC)
        """)

        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_task_assignments_assignee
            ON task_assignments(assignee, task_status)
        """)

        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_tasks_task_id
            ON tasks(task_id)
        """)

        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_tasks_assignee
            ON tasks(assignee, task_status)
        """)

        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_collaboration_records_document_id
            ON collaboration_records(document_id, action_time DESC)
        """)

        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_collaboration_records_user_id
            ON collaboration_records(user_id, action_time DESC)
        """)

        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_document_permissions_document_id
            ON document_permissions(document_id)
        """)

        self.conn.commit()

    def store_document(self, document_data: Dict) -> int:
        """存储文档"""
        self.cur.execute("""
            INSERT INTO documents (
                document_id, document_title, document_type,
                author, file_path, file_size, mime_type, current_version
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (document_id) DO UPDATE SET
                document_title = EXCLUDED.document_title,
                updated_at = CURRENT_TIMESTAMP
            RETURNING id
        """, (
            document_data.get("document_id"),
            document_data.get("document_title"),
            document_data.get("document_type"),
            document_data.get("author"),
            document_data.get("file_path"),
            document_data.get("file_size"),
            document_data.get("mime_type"),
            document_data.get("current_version", 1)
        ))
        return self.cur.fetchone()[0]

    def store_process_approval(self, process_data: Dict) -> int:
        """存储流程审批"""
        self.cur.execute("""
            INSERT INTO process_approvals (
                process_id, process_name, process_type,
                submitter, current_status, submit_time, process_data
            ) VALUES (%s, %s, %s, %s, %s, %s, %s::jsonb)
            ON CONFLICT (process_id) DO UPDATE SET
                current_status = EXCLUDED.current_status,
                updated_at = CURRENT_TIMESTAMP
            RETURNING id
        """, (
            process_data.get("process_id"),
            process_data.get("process_name"),
            process_data.get("process_type"),
            process_data.get("submitter"),
            process_data.get("current_status"),
            process_data.get("submit_time"),
            json.dumps(process_data.get("process_data", {}))
        ))
        self.conn.commit()
        return self.cur.fetchone()[0]

    def update_process_status(self, process_id: str, status: str, current_node: str = None):
        """更新流程状态"""
        if current_node:
            self.cur.execute("""
                UPDATE process_approvals
                SET current_status = %s, current_node = %s, updated_at = CURRENT_TIMESTAMP
                WHERE process_id = %s
            """, (status, current_node, process_id))
        else:
            self.cur.execute("""
                UPDATE process_approvals
                SET current_status = %s, updated_at = CURRENT_TIMESTAMP
                WHERE process_id = %s
            """, (status, process_id))
        self.conn.commit()

    def store_approval_record(self, approval_data: Dict) -> int:
        """存储审批记录"""
        self.cur.execute("""
            INSERT INTO approval_records (
                process_id, node_id, approver, approval_result,
                approval_comment, approval_time
            ) VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            approval_data.get("process_id"),
            approval_data.get("node_id"),
            approval_data.get("approver"),
            approval_data.get("approval_result"),
            approval_data.get("approval_comment"),
            approval_data.get("approval_time")
        ))
        self.conn.commit()
        return self.cur.fetchone()[0]

    def store_document_version(self, version_data: Dict) -> int:
        """存储文档版本"""
        self.cur.execute("""
            INSERT INTO document_versions (
                document_id, version_number, version_author,
                version_comment, version_file_path
            ) VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """, (
            version_data.get("document_id"),
            version_data.get("version_number"),
            version_data.get("version_author"),
            version_data.get("version_comment"),
            version_data.get("version_file_path")
        ))
        self.conn.commit()
        return self.cur.fetchone()[0]

    def get_current_version(self, document_id: str) -> int:
        """获取文档当前版本"""
        self.cur.execute("""
            SELECT current_version FROM documents WHERE document_id = %s
        """, (document_id,))
        result = self.cur.fetchone()
        return result[0] if result else 1

    def update_document_version(self, document_id: str, version: int):
        """更新文档版本"""
        self.cur.execute("""
            UPDATE documents
            SET current_version = %s, updated_at = CURRENT_TIMESTAMP
            WHERE document_id = %s
        """, (version, document_id))
        self.conn.commit()

    def get_document_versions(self, document_id: str) -> List[Dict]:
        """获取文档版本历史"""
        self.cur.execute("""
            SELECT version_number, version_author, version_comment,
                   version_file_path, created_at
            FROM document_versions
            WHERE document_id = %s
            ORDER BY version_number DESC
        """, (document_id,))
        return [
            {
                "version_number": row[0],
                "version_author": row[1],
                "version_comment": row[2],
                "version_file_path": row[3],
                "created_at": row[4]
            }
            for row in self.cur.fetchall()
        ]

    def get_document_version(self, document_id: str, version_number: int) -> Optional[Dict]:
        """获取指定版本"""
        self.cur.execute("""
            SELECT version_number, version_author, version_comment,
                   version_file_path, created_at
            FROM document_versions
            WHERE document_id = %s AND version_number = %s
        """, (document_id, version_number))
        row = self.cur.fetchone()
        if row:
            return {
                "version_number": row[0],
                "version_author": row[1],
                "version_comment": row[2],
                "version_file_path": row[3],
                "created_at": row[4]
            }
        return None

    def store_document_content(self, document_id: str, version_number: int,
                              content_text: str = None, content_html: str = None,
                              content_json: Dict = None) -> int:
        """存储文档内容"""
        self.cur.execute("""
            INSERT INTO document_contents (
                document_id, version_number, content_text,
                content_html, content_json
            ) VALUES (%s, %s, %s, %s, %s::jsonb)
            ON CONFLICT (document_id, version_number) DO UPDATE SET
                content_text = EXCLUDED.content_text,
                content_html = EXCLUDED.content_html,
                content_json = EXCLUDED.content_json,
                extracted_at = CURRENT_TIMESTAMP
            RETURNING id
        """, (
            document_id, version_number, content_text,
            content_html, json.dumps(content_json) if content_json else None
        ))
        self.conn.commit()
        return self.cur.fetchone()[0]

    def search_documents_fulltext(self, search_query: str, limit: int = 100) -> List[Dict]:
        """全文搜索文档"""
        self.cur.execute("""
            SELECT DISTINCT d.document_id, d.document_title, d.document_type,
                   d.author, d.created_at, dc.version_number,
                   ts_rank(to_tsvector('english', dc.content_text),
                          plainto_tsquery('english', %s)) as rank
            FROM documents d
            JOIN document_contents dc ON d.document_id = dc.document_id
            WHERE to_tsvector('english', dc.content_text) @@ plainto_tsquery('english', %s)
            ORDER BY rank DESC, d.created_at DESC
            LIMIT %s
        """, (search_query, search_query, limit))

        return [
            {
                "document_id": row[0],
                "document_title": row[1],
                "document_type": row[2],
                "author": row[3],
                "created_at": row[4],
                "version_number": row[5],
                "rank": float(row[6])
            }
            for row in self.cur.fetchall()
        ]

    def store_task_assignment(self, assignment_data: Dict) -> int:
        """存储任务分配"""
        self.cur.execute("""
            INSERT INTO task_assignments (
                process_id, node_id, assignee, assigned_time, task_status
            ) VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """, (
            assignment_data.get("process_id"),
            assignment_data.get("node_id"),
            assignment_data.get("assignee"),
            assignment_data.get("assigned_time"),
            assignment_data.get("task_status", "Assigned")
        ))
        self.conn.commit()
        return self.cur.fetchone()[0]

    def get_pending_tasks(self, process_id: str) -> List[Dict]:
        """获取待处理任务"""
        self.cur.execute("""
            SELECT process_id, node_id, assignee, assigned_time, task_status
            FROM task_assignments
            WHERE process_id = %s AND task_status IN ('Assigned', 'InProgress')
            ORDER BY assigned_time DESC
        """, (process_id,))

        return [
            {
                "process_id": row[0],
                "node_id": row[1],
                "assignee": row[2],
                "assigned_time": row[3],
                "task_status": row[4]
            }
            for row in self.cur.fetchall()
        ]

    def get_completed_tasks(self, process_id: str) -> List[Dict]:
        """获取已完成任务"""
        self.cur.execute("""
            SELECT process_id, node_id, assignee, assigned_time,
                   completed_time, task_status
            FROM task_assignments
            WHERE process_id = %s AND task_status = 'Completed'
            ORDER BY completed_time DESC
        """, (process_id,))

        return [
            {
                "process_id": row[0],
                "node_id": row[1],
                "assignee": row[2],
                "assigned_time": row[3],
                "completed_time": row[4],
                "task_status": row[5]
            }
            for row in self.cur.fetchall()
        ]

    def store_collaboration_record(self, document_id: str, user_id: str,
                                   action_type: str, action_description: str = None,
                                   action_data: Dict = None) -> int:
        """存储协作记录"""
        self.cur.execute("""
            INSERT INTO collaboration_records (
                document_id, user_id, action_type,
                action_description, action_data
            ) VALUES (%s, %s, %s, %s, %s::jsonb)
            RETURNING id
        """, (
            document_id, user_id, action_type,
            action_description, json.dumps(action_data) if action_data else None
        ))
        self.conn.commit()
        return self.cur.fetchone()[0]

    def get_collaboration_history(self, document_id: str, limit: int = 100) -> List[Dict]:
        """获取协作历史"""
        self.cur.execute("""
            SELECT user_id, action_type, action_description,
                   action_data, action_time
            FROM collaboration_records
            WHERE document_id = %s
            ORDER BY action_time DESC
            LIMIT %s
        """, (document_id, limit))

        return [
            {
                "user_id": row[0],
                "action_type": row[1],
                "action_description": row[2],
                "action_data": json.loads(row[3]) if row[3] else None,
                "action_time": row[4]
            }
            for row in self.cur.fetchall()
        ]

    def grant_document_permission(self, document_id: str, user_id: str,
                                  permission_type: str, granted_by: str) -> int:
        """授予文档权限"""
        self.cur.execute("""
            INSERT INTO document_permissions (
                document_id, user_id, permission_type, granted_by
            ) VALUES (%s, %s, %s, %s)
            ON CONFLICT (document_id, user_id, permission_type) DO UPDATE SET
                granted_by = EXCLUDED.granted_by,
                granted_at = CURRENT_TIMESTAMP
            RETURNING id
        """, (document_id, user_id, permission_type, granted_by))
        self.conn.commit()
        return self.cur.fetchone()[0]

    def check_document_permission(self, document_id: str, user_id: str,
                                 permission_type: str) -> bool:
        """检查文档权限"""
        self.cur.execute("""
            SELECT COUNT(*) FROM document_permissions
            WHERE document_id = %s AND user_id = %s AND permission_type = %s
        """, (document_id, user_id, permission_type))
        return self.cur.fetchone()[0] > 0

    def store_process_instance(self, instance_data: Dict) -> int:
        """存储流程实例"""
        self.cur.execute("""
            INSERT INTO process_instances (
                instance_id, process_id, process_name, submitter,
                current_status, current_node, submit_time,
                process_data, nodes_history
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s::jsonb, %s::jsonb)
            ON CONFLICT (instance_id) DO UPDATE SET
                current_status = EXCLUDED.current_status,
                current_node = EXCLUDED.current_node,
                process_data = EXCLUDED.process_data,
                nodes_history = EXCLUDED.nodes_history,
                updated_at = CURRENT_TIMESTAMP
            RETURNING id
        """, (
            instance_data.get("instance_id"),
            instance_data.get("process_id"),
            instance_data.get("process_name"),
            instance_data.get("submitter"),
            instance_data.get("current_status"),
            instance_data.get("current_node"),
            instance_data.get("submit_time"),
            json.dumps(instance_data.get("process_data", {})),
            json.dumps(instance_data.get("nodes_history", []))
        ))
        self.conn.commit()
        return self.cur.fetchone()[0]

    def update_process_instance(self, instance_id: str, status: str = None,
                               current_node: str = None, complete_time: datetime = None):
        """更新流程实例"""
        updates = []
        params = []

        if status:
            updates.append("current_status = %s")
            params.append(status)

        if current_node:
            updates.append("current_node = %s")
            params.append(current_node)

        if complete_time:
            updates.append("complete_time = %s")
            params.append(complete_time)
            # 计算持续时间
            self.cur.execute("""
                SELECT submit_time FROM process_instances WHERE instance_id = %s
            """, (instance_id,))
            submit_time = self.cur.fetchone()
            if submit_time:
                duration = (complete_time - submit_time[0]).total_seconds() / 3600
                updates.append("duration_hours = %s")
                params.append(duration)

        if updates:
            updates.append("updated_at = CURRENT_TIMESTAMP")
            params.append(instance_id)

            query = f"""
                UPDATE process_instances
                SET {', '.join(updates)}
                WHERE instance_id = %s
            """
            self.cur.execute(query, tuple(params))
            self.conn.commit()

    def close(self):
        """关闭数据库连接"""
        self.cur.close()
        self.conn.close()
```

### 7.2 OA数据分析查询

**查询示例**：

```python
    def get_document_statistics(self, start_date: datetime) -> List[Dict]:
        """查询文档统计"""
        self.cur.execute("""
            SELECT
                document_type,
                COUNT(*) as count,
                SUM(file_size) as total_size,
                AVG(file_size) as avg_size,
                MAX(file_size) as max_size,
                MIN(file_size) as min_size
            FROM documents
            WHERE created_at >= %s
            GROUP BY document_type
            ORDER BY count DESC
        """, (start_date,))
        return [
            {
                "document_type": row[0],
                "count": row[1],
                "total_size": row[2],
                "avg_size": float(row[3]) if row[3] else 0,
                "max_size": row[4],
                "min_size": row[5]
            }
            for row in self.cur.fetchall()
        ]

    def get_process_statistics(self, days: int = 30) -> List[Dict]:
        """查询流程审批统计"""
        self.cur.execute("""
            SELECT
                process_type,
                current_status,
                COUNT(*) as count,
                AVG(EXTRACT(EPOCH FROM (complete_time - submit_time))/3600) as avg_hours,
                MIN(EXTRACT(EPOCH FROM (complete_time - submit_time))/3600) as min_hours,
                MAX(EXTRACT(EPOCH FROM (complete_time - submit_time))/3600) as max_hours
            FROM process_approvals
            WHERE submit_time >= CURRENT_TIMESTAMP - INTERVAL '%s days'
            AND complete_time IS NOT NULL
            GROUP BY process_type, current_status
            ORDER BY process_type, current_status
        """, (days,))
        return [
            {
                "process_type": row[0],
                "current_status": row[1],
                "count": row[2],
                "avg_hours": float(row[3]) if row[3] else None,
                "min_hours": float(row[4]) if row[4] else None,
                "max_hours": float(row[5]) if row[5] else None
            }
            for row in self.cur.fetchall()
        ]

    def get_task_statistics(self, assignee: str = None, days: int = 30) -> Dict:
        """查询任务统计"""
        if assignee:
            self.cur.execute("""
                SELECT
                    task_status,
                    COUNT(*) as count,
                    COUNT(CASE WHEN due_date < CURRENT_TIMESTAMP THEN 1 END) as overdue_count
                FROM tasks
                WHERE assignee = %s
                AND created_at >= CURRENT_TIMESTAMP - INTERVAL '%s days'
                GROUP BY task_status
            """, (assignee, days))
        else:
            self.cur.execute("""
                SELECT
                    task_status,
                    COUNT(*) as count,
                    COUNT(CASE WHEN due_date < CURRENT_TIMESTAMP THEN 1 END) as overdue_count
                FROM tasks
                WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL '%s days'
                GROUP BY task_status
            """, (days,))

        stats = {}
        for row in self.cur.fetchall():
            stats[row[0]] = {
                "count": row[1],
                "overdue_count": row[2]
            }

        return stats

    def get_process_approval_history(self, process_id: str) -> List[Dict]:
        """查询流程审批历史"""
        self.cur.execute("""
            SELECT
                node_id,
                approver,
                approval_result,
                approval_comment,
                approval_time
            FROM approval_records
            WHERE process_id = %s
            ORDER BY approval_time ASC
        """, (process_id,))
        return [
            {
                "node_id": row[0],
                "approver": row[1],
                "approval_result": row[2],
                "approval_comment": row[3],
                "approval_time": row[4]
            }
            for row in self.cur.fetchall()
        ]

    def get_user_workload(self, user: str, days: int = 7) -> Dict:
        """查询用户工作量"""
        # 查询任务数量
        self.cur.execute("""
            SELECT
                COUNT(*) as total_tasks,
                COUNT(CASE WHEN task_status = 'InProgress' THEN 1 END) as in_progress_tasks,
                COUNT(CASE WHEN task_status = 'Completed' THEN 1 END) as completed_tasks,
                COUNT(CASE WHEN due_date < CURRENT_TIMESTAMP AND task_status != 'Completed' THEN 1 END) as overdue_tasks
            FROM tasks
            WHERE assignee = %s
            AND created_at >= CURRENT_TIMESTAMP - INTERVAL '%s days'
        """, (user, days))
        task_stats = self.cur.fetchone()

        # 查询审批数量
        self.cur.execute("""
            SELECT
                COUNT(*) as total_approvals,
                COUNT(CASE WHEN current_status = 'InProgress' THEN 1 END) as pending_approvals
            FROM process_approvals
            WHERE submitter = %s
            AND submit_time >= CURRENT_TIMESTAMP - INTERVAL '%s days'
        """, (user, days))
        approval_stats = self.cur.fetchone()

        return {
            "user": user,
            "tasks": {
                "total": task_stats[0],
                "in_progress": task_stats[1],
                "completed": task_stats[2],
                "overdue": task_stats[3]
            },
            "approvals": {
                "total": approval_stats[0],
                "pending": approval_stats[1]
            }
        }
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21
