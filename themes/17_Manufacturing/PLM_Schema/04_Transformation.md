# PLM Schema转换体系

## 📑 目录

- [PLM Schema转换体系](#plm-schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
    - [1.1 转换目标](#11-转换目标)
  - [2. STEP文件解析实现](#2-step文件解析实现)
    - [2.1 STEP文件解析器](#21-step文件解析器)
    - [2.2 STEP实体解析器](#22-step实体解析器)
  - [3. CAD集成实现](#3-cad集成实现)
    - [3.1 CAD文件解析器](#31-cad文件解析器)
    - [3.2 CAD格式转换器](#32-cad格式转换器)
  - [4. BOM管理实现](#4-bom管理实现)
    - [4.1 BOM解析器](#41-bom解析器)
    - [4.2 BOM到ERP转换](#42-bom到erp转换)
  - [5. PLM数据存储与分析](#5-plm数据存储与分析)
    - [5.1 PostgreSQL PLM数据存储](#51-postgresql-plm数据存储)
    - [5.2 PLM数据分析查询](#52-plm数据分析查询)

---

## 1. 转换体系概述

PLM Schema转换体系支持STEP文件、CAD文件、
BOM数据、数据库存储之间的转换。

### 1.1 转换目标

1. **STEP文件解析**：STEP文件到数据库存储
2. **CAD集成**：CAD文件解析和格式转换
3. **BOM管理**：BOM创建、版本管理、结构管理
4. **数据到数据库转换**：PLM数据到PostgreSQL存储

---

## 2. STEP文件解析实现

### 2.1 STEP文件解析器

**完整的STEP文件解析实现**：

```python
import logging
import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

class STEPParser:
    """STEP文件解析器"""

    def __init__(self):
        self.header_pattern = re.compile(r'HEADER;')
        self.data_pattern = re.compile(r'DATA;')
        self.end_pattern = re.compile(r'ENDSEC;')
        self.entity_pattern = re.compile(r'#(\d+)\s*=\s*([A-Z_]+)\s*\(([^)]*)\);')

    def parse_step_file(self, file_path: str) -> Dict:
        """解析STEP文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 解析文件结构
            header_end = content.find('ENDSEC;')
            data_start = content.find('DATA;')
            data_end = content.find('ENDSEC;', data_start)

            # 解析HEADER段
            header_section = content[:header_end + len('ENDSEC;')]
            header_data = self._parse_header(header_section)

            # 解析DATA段
            data_section = content[data_start:data_end + len('ENDSEC;')]
            entities = self._parse_data(data_section)

            return {
                "file_path": file_path,
                "step_header": header_data,
                "step_data": {
                    "entities": entities
                },
                "step_end": {
                    "end_marker": "ENDSTEP"
                }
            }
        except Exception as e:
            logger.error(f"Error parsing STEP file: {e}")
            raise

    def _parse_header(self, header_section: str) -> Dict:
        """解析HEADER段"""
        header_data = {}

        # 解析文件描述
        file_desc_match = re.search(r'FILE_DESCRIPTION\s*\(([^)]+)\)', header_section)
        if file_desc_match:
            desc_content = file_desc_match.group(1)
            parts = [p.strip().strip('"') for p in desc_content.split(',')]
            header_data["file_description"] = parts[0] if parts else ""

        # 解析文件名
        file_name_match = re.search(r'FILE_NAME\s*\(([^)]+)\)', header_section)
        if file_name_match:
            name_content = file_name_match.group(1)
            parts = [p.strip().strip('"') for p in name_content.split(',')]
            header_data["file_name"] = parts[0] if parts else ""
            header_data["file_author"] = parts[2] if len(parts) > 2 else ""
            header_data["file_organization"] = parts[3] if len(parts) > 3 else ""

        # 解析文件Schema
        file_schema_match = re.search(r'FILE_SCHEMA\s*\(([^)]+)\)', header_section)
        if file_schema_match:
            schema_content = file_schema_match.group(1)
            schemas = [s.strip().strip('"') for s in schema_content.split(',')]
            header_data["file_schema"] = schemas[0] if schemas else ""

        return header_data

    def _parse_data(self, data_section: str) -> List[Dict]:
        """解析DATA段"""
        entities = []

        # 查找所有实体
        matches = self.entity_pattern.finditer(data_section)
        for match in matches:
            entity_id = int(match.group(1))
            entity_type = match.group(2)
            entity_params = match.group(3)

            # 解析实体参数
            params = self._parse_entity_params(entity_params)

            entities.append({
                "entity_id": entity_id,
                "entity_type": entity_type,
                "entity_data": params
            })

        return entities

    def _parse_entity_params(self, params_str: str) -> Dict:
        """解析实体参数"""
        params = {}

        # 简单的参数解析（实际实现需要更复杂的解析逻辑）
        if params_str:
            # 移除引号和空格
            cleaned = params_str.strip()
            if cleaned.startswith('"') and cleaned.endswith('"'):
                params["value"] = cleaned[1:-1]
            elif cleaned.startswith('(') and cleaned.endswith(')'):
                # 列表参数
                inner = cleaned[1:-1]
                params["values"] = [v.strip().strip('"') for v in inner.split(',')]
            else:
                params["value"] = cleaned

        return params
```

### 2.2 STEP实体解析器

**STEP实体详细解析实现**：

```python
class STEPEntityParser:
    """STEP实体解析器"""

    def __init__(self):
        self.parsers = {
            "PRODUCT": self._parse_product,
            "PRODUCT_DEFINITION": self._parse_product_definition,
            "SHAPE_REPRESENTATION": self._parse_shape_representation,
            "CARTESIAN_POINT": self._parse_cartesian_point,
            "DIRECTION": self._parse_direction
        }

    def parse_entity(self, entity: Dict) -> Dict:
        """解析实体"""
        entity_type = entity.get("entity_type")
        parser = self.parsers.get(entity_type)

        if parser:
            return parser(entity)
        else:
            return entity

    def _parse_product(self, entity: Dict) -> Dict:
        """解析PRODUCT实体"""
        data = entity.get("entity_data", {})
        return {
            "entity_type": "PRODUCT",
            "id": entity.get("entity_id"),
            "name": data.get("value", ""),
            "description": data.get("description", "")
        }

    def _parse_product_definition(self, entity: Dict) -> Dict:
        """解析PRODUCT_DEFINITION实体"""
        return {
            "entity_type": "PRODUCT_DEFINITION",
            "id": entity.get("entity_id"),
            "definition_id": entity.get("entity_data", {}).get("value", "")
        }

    def _parse_shape_representation(self, entity: Dict) -> Dict:
        """解析SHAPE_REPRESENTATION实体"""
        return {
            "entity_type": "SHAPE_REPRESENTATION",
            "id": entity.get("entity_id"),
            "name": entity.get("entity_data", {}).get("value", "")
        }

    def _parse_cartesian_point(self, entity: Dict) -> Dict:
        """解析CARTESIAN_POINT实体"""
        data = entity.get("entity_data", {})
        values = data.get("values", [])
        return {
            "entity_type": "CARTESIAN_POINT",
            "id": entity.get("entity_id"),
            "x": float(values[0]) if len(values) > 0 else 0.0,
            "y": float(values[1]) if len(values) > 1 else 0.0,
            "z": float(values[2]) if len(values) > 2 else 0.0
        }

    def _parse_direction(self, entity: Dict) -> Dict:
        """解析DIRECTION实体"""
        data = entity.get("entity_data", {})
        values = data.get("values", [])
        return {
            "entity_type": "DIRECTION",
            "id": entity.get("entity_id"),
            "x": float(values[0]) if len(values) > 0 else 0.0,
            "y": float(values[1]) if len(values) > 1 else 0.0,
            "z": float(values[2]) if len(values) > 2 else 0.0
        }
```

---

## 3. CAD集成实现

### 3.1 CAD文件解析器

**完整的CAD文件解析实现**：

```python
import os
from typing import Dict, List, Optional

class CADFileParser:
    """CAD文件解析器"""

    def __init__(self):
        self.supported_formats = {
            '.step': self._parse_step,
            '.stp': self._parse_step,
            '.iges': self._parse_iges,
            '.igs': self._parse_iges,
            '.jt': self._parse_jt,
            '.x_t': self._parse_parasolid,
            '.x_b': self._parse_parasolid
        }

    def parse_cad_file(self, file_path: str) -> Dict:
        """解析CAD文件"""
        file_ext = os.path.splitext(file_path)[1].lower()

        parser = self.supported_formats.get(file_ext)
        if not parser:
            raise ValueError(f"Unsupported CAD file format: {file_ext}")

        return parser(file_path)

    def _parse_step(self, file_path: str) -> Dict:
        """解析STEP文件"""
        step_parser = STEPParser()
        step_data = step_parser.parse_step_file(file_path)

        return {
            "file_path": file_path,
            "file_format": "STEP",
            "model_type": self._detect_model_type(step_data),
            "entities": step_data.get("step_data", {}).get("entities", []),
            "metadata": step_data.get("step_header", {})
        }

    def _parse_iges(self, file_path: str) -> Dict:
        """解析IGES文件"""
        # IGES文件解析实现（简化版）
        return {
            "file_path": file_path,
            "file_format": "IGES",
            "model_type": "Part",
            "entities": [],
            "metadata": {}
        }

    def _parse_jt(self, file_path: str) -> Dict:
        """解析JT文件"""
        # JT文件解析实现（简化版）
        return {
            "file_path": file_path,
            "file_format": "JT",
            "model_type": "Assembly",
            "entities": [],
            "metadata": {}
        }

    def _parse_parasolid(self, file_path: str) -> Dict:
        """解析Parasolid文件"""
        # Parasolid文件解析实现（简化版）
        return {
            "file_path": file_path,
            "file_format": "Parasolid",
            "model_type": "Part",
            "entities": [],
            "metadata": {}
        }

    def _detect_model_type(self, step_data: Dict) -> str:
        """检测模型类型"""
        entities = step_data.get("step_data", {}).get("entities", [])

        # 检查是否有装配体相关实体
        for entity in entities:
            if entity.get("entity_type") in ["NEXT_ASSEMBLY_USAGE_OCCURRENCE", "PRODUCT_DEFINITION_FORMATION"]:
                return "Assembly"

        return "Part"
```

### 3.2 CAD格式转换器

**CAD格式转换器实现**：

```python
class CADFormatConverter:
    """CAD格式转换器"""

    def __init__(self):
        self.parser = CADFileParser()

    def convert_cad_file(self, source_path: str, target_format: str, target_path: str) -> bool:
        """转换CAD文件格式"""
        try:
            # 解析源文件
            source_data = self.parser.parse_cad_file(source_path)

            # 转换为目标格式
            if target_format.upper() == "STEP":
                return self._convert_to_step(source_data, target_path)
            elif target_format.upper() == "IGES":
                return self._convert_to_iges(source_data, target_path)
            elif target_format.upper() == "JT":
                return self._convert_to_jt(source_data, target_path)
            else:
                raise ValueError(f"Unsupported target format: {target_format}")
        except Exception as e:
            logger.error(f"Error converting CAD file: {e}")
            return False

    def _convert_to_step(self, source_data: Dict, target_path: str) -> bool:
        """转换为STEP格式"""
        try:
            with open(target_path, 'w', encoding='utf-8') as f:
                # 写入HEADER段
                f.write("ISO-10303-21;\n")
                f.write("HEADER;\n")
                f.write(f"FILE_DESCRIPTION(('{source_data.get('metadata', {}).get('file_description', '')}'), '2;1');\n")
                f.write(f"FILE_NAME('{os.path.basename(target_path)}', '{datetime.now().isoformat()}', "
                       f"('{source_data.get('metadata', {}).get('file_author', '')}'), "
                       f"('{source_data.get('metadata', {}).get('file_organization', '')}'), "
                       f"'STEP PARSER', 'NONE', 'NONE');\n")
                f.write(f"FILE_SCHEMA(('{source_data.get('metadata', {}).get('file_schema', 'AUTOMOTIVE_DESIGN')}'));\n")
                f.write("ENDSEC;\n")

                # 写入DATA段
                f.write("DATA;\n")
                entities = source_data.get("entities", [])
                for entity in entities:
                    entity_id = entity.get("entity_id", 0)
                    entity_type = entity.get("entity_type", "UNKNOWN")
                    f.write(f"#{entity_id} = {entity_type}();\n")
                f.write("ENDSEC;\n")
                f.write("END-ISO-10303-21;\n")

            return True
        except Exception as e:
            logger.error(f"Error converting to STEP: {e}")
            return False

    def _convert_to_iges(self, source_data: Dict, target_path: str) -> bool:
        """转换为IGES格式"""
        # IGES转换实现（简化版）
        return False

    def _convert_to_jt(self, source_data: Dict, target_path: str) -> bool:
        """转换为JT格式"""
        # JT转换实现（简化版）
        return False
```

---

## 4. BOM管理实现

### 4.1 BOM解析器

**完整的BOM解析实现**：

```python
from typing import Dict, List, Optional
from decimal import Decimal

class BOMParser:
    """BOM解析器"""

    def __init__(self):
        pass

    def parse_bom_data(self, bom_data: Dict) -> Dict:
        """解析BOM数据"""
        return {
            "bom_id": bom_data.get("bom_id"),
            "bom_number": bom_data.get("bom_number"),
            "product_id": bom_data.get("product_id"),
            "bom_info": {
                "bom_type": bom_data.get("bom_type", "Manufacturing"),
                "bom_version": bom_data.get("bom_version", "1.0"),
                "bom_status": bom_data.get("bom_status", "Active"),
                "effective_date": bom_data.get("effective_date"),
                "creator": bom_data.get("creator")
            },
            "bom_structure": {
                "bom_items": self._parse_bom_items(bom_data.get("bom_items", []))
            },
            "material_info": {
                "materials": self._parse_materials(bom_data.get("materials", []))
            }
        }

    def _parse_bom_items(self, items: List[Dict]) -> List[Dict]:
        """解析BOM项"""
        parsed_items = []
        for item in items:
            parsed_items.append({
                "item_id": item.get("item_id"),
                "material_id": item.get("material_id"),
                "material_name": item.get("material_name"),
                "level": item.get("level", 0),
                "parent_item_id": item.get("parent_item_id"),
                "quantity": Decimal(str(item.get("quantity", 0))),
                "unit": item.get("unit", "pieces"),
                "usage_type": item.get("usage_type", "Normal"),
                "sequence": item.get("sequence", 0)
            })
        return parsed_items

    def _parse_materials(self, materials: List[Dict]) -> List[Dict]:
        """解析物料信息"""
        parsed_materials = []
        for material in materials:
            parsed_materials.append({
                "material_id": material.get("material_id"),
                "material_number": material.get("material_number"),
                "material_name": material.get("material_name"),
                "material_type": material.get("material_type"),
                "material_specification": material.get("material_specification"),
                "unit": material.get("unit", "pieces")
            })
        return parsed_materials
```

### 4.2 BOM到ERP转换

**BOM到ERP转换器实现**：

```python
class BOMToERPConverter:
    """BOM到ERP转换器"""

    def __init__(self):
        self.parser = BOMParser()

    def convert_bom_to_erp(self, bom_data: Dict) -> Dict:
        """将BOM转换为ERP格式"""
        bom = self.parser.parse_bom_data(bom_data)

        erp_bom = {
            "bom_number": bom["bom_number"],
            "product_id": bom["product_id"],
            "bom_type": bom["bom_info"]["bom_type"],
            "bom_version": bom["bom_info"]["bom_version"],
            "effective_date": bom["bom_info"]["effective_date"],
            "bom_items": []
        }

        # 转换BOM项
        for item in bom["bom_structure"]["bom_items"]:
            erp_item = {
                "material_id": item["material_id"],
                "material_number": self._get_material_number(bom, item["material_id"]),
                "material_name": item["material_name"],
                "quantity": float(item["quantity"]),
                "unit": item["unit"],
                "level": item["level"],
                "parent_material_id": self._get_parent_material_id(bom, item["parent_item_id"])
            }
            erp_bom["bom_items"].append(erp_item)

        return erp_bom

    def _get_material_number(self, bom: Dict, material_id: str) -> str:
        """获取物料编号"""
        for material in bom["material_info"]["materials"]:
            if material["material_id"] == material_id:
                return material["material_number"]
        return ""

    def _get_parent_material_id(self, bom: Dict, parent_item_id: Optional[str]) -> Optional[str]:
        """获取父物料ID"""
        if not parent_item_id:
            return None

        for item in bom["bom_structure"]["bom_items"]:
            if item["item_id"] == parent_item_id:
                return item["material_id"]
        return None
```

---

## 5. PLM数据存储与分析

### 5.1 PostgreSQL PLM数据存储

**完整的PostgreSQL存储实现**：

```python
import psycopg2
import json
from typing import Dict, List, Optional
from datetime import datetime

class PLMStorage:
    """PLM数据存储系统"""

    def __init__(self, connection_string: str):
        self.conn = psycopg2.connect(connection_string)
        self.cur = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        """创建PLM数据表"""
        # 产品设计表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS product_designs (
                id BIGSERIAL PRIMARY KEY,
                product_id VARCHAR(20) UNIQUE NOT NULL,
                product_number VARCHAR(50) UNIQUE NOT NULL,
                product_name VARCHAR(200) NOT NULL,
                product_type VARCHAR(100) NOT NULL,
                design_stage VARCHAR(50) NOT NULL,
                design_status VARCHAR(50) NOT NULL,
                designer VARCHAR(100) NOT NULL,
                design_date DATE NOT NULL,
                version VARCHAR(20) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # CAD模型表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS cad_models (
                id BIGSERIAL PRIMARY KEY,
                model_id VARCHAR(20) UNIQUE NOT NULL,
                product_id VARCHAR(20) NOT NULL,
                model_name VARCHAR(200) NOT NULL,
                model_type VARCHAR(50) NOT NULL,
                file_format VARCHAR(50) NOT NULL,
                file_path VARCHAR(500) NOT NULL,
                model_version VARCHAR(20) NOT NULL,
                created_date DATE,
                FOREIGN KEY (product_id) REFERENCES product_designs(product_id)
            )
        """)

        # 变更管理表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS change_management (
                id BIGSERIAL PRIMARY KEY,
                change_id VARCHAR(20) UNIQUE NOT NULL,
                change_number VARCHAR(50) UNIQUE NOT NULL,
                requestor VARCHAR(100) NOT NULL,
                request_date TIMESTAMP NOT NULL,
                change_type VARCHAR(50) NOT NULL,
                change_reason VARCHAR(500) NOT NULL,
                change_description TEXT NOT NULL,
                priority VARCHAR(20) DEFAULT 'Normal',
                overall_status VARCHAR(50) NOT NULL,
                approval_date TIMESTAMP,
                execution_status VARCHAR(50) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # BOM表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS boms (
                id BIGSERIAL PRIMARY KEY,
                bom_id VARCHAR(20) UNIQUE NOT NULL,
                bom_number VARCHAR(50) UNIQUE NOT NULL,
                product_id VARCHAR(20) NOT NULL,
                bom_type VARCHAR(50) NOT NULL,
                bom_version VARCHAR(20) NOT NULL,
                bom_status VARCHAR(50) NOT NULL,
                effective_date DATE NOT NULL,
                expiry_date DATE,
                creator VARCHAR(100) NOT NULL,
                created_date DATE NOT NULL,
                FOREIGN KEY (product_id) REFERENCES product_designs(product_id)
            )
        """)

        # BOM项表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS bom_items (
                id BIGSERIAL PRIMARY KEY,
                item_id VARCHAR(20) UNIQUE NOT NULL,
                bom_id VARCHAR(20) NOT NULL,
                material_id VARCHAR(20) NOT NULL,
                material_name VARCHAR(200) NOT NULL,
                level INTEGER NOT NULL,
                parent_item_id VARCHAR(20),
                quantity DECIMAL(10,4) NOT NULL,
                unit VARCHAR(20) NOT NULL,
                usage_type VARCHAR(50) DEFAULT 'Normal',
                sequence INTEGER NOT NULL,
                FOREIGN KEY (bom_id) REFERENCES boms(bom_id)
            )
        """)

        # 创建索引
        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_product_designs_product_id
            ON product_designs(product_id)
        """)

        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_cad_models_product_id
            ON cad_models(product_id)
        """)

        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_bom_items_bom_id
            ON bom_items(bom_id, level)
        """)

        self.conn.commit()

    def store_product_design(self, design_data: Dict) -> int:
        """存储产品设计"""
        self.cur.execute("""
            INSERT INTO product_designs (
                product_id, product_number, product_name, product_type,
                design_stage, design_status, designer, design_date, version
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (product_id) DO UPDATE SET
                design_status = EXCLUDED.design_status,
                updated_at = CURRENT_TIMESTAMP
            RETURNING id
        """, (
            design_data.get("product_id"),
            design_data.get("product_number"),
            design_data.get("product_name"),
            design_data.get("product_info", {}).get("product_type"),
            design_data.get("product_info", {}).get("design_stage"),
            design_data.get("product_info", {}).get("design_status"),
            design_data.get("product_info", {}).get("designer"),
            design_data.get("product_info", {}).get("design_date"),
            design_data.get("product_info", {}).get("version")
        ))
        self.conn.commit()
        return self.cur.fetchone()[0]

    def store_cad_model(self, model_data: Dict) -> int:
        """存储CAD模型"""
        self.cur.execute("""
            INSERT INTO cad_models (
                model_id, product_id, model_name, model_type,
                file_format, file_path, model_version, created_date
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (model_id) DO UPDATE SET
                model_version = EXCLUDED.model_version
            RETURNING id
        """, (
            model_data.get("model_id"),
            model_data.get("product_id"),
            model_data.get("model_name"),
            model_data.get("model_type"),
            model_data.get("file_format"),
            model_data.get("file_path"),
            model_data.get("model_version"),
            model_data.get("created_date")
        ))
        self.conn.commit()
        return self.cur.fetchone()[0]

    def store_change_management(self, change_data: Dict) -> int:
        """存储变更管理"""
        self.cur.execute("""
            INSERT INTO change_management (
                change_id, change_number, requestor, request_date,
                change_type, change_reason, change_description, priority,
                overall_status, approval_date, execution_status
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (change_id) DO UPDATE SET
                overall_status = EXCLUDED.overall_status,
                execution_status = EXCLUDED.execution_status,
                updated_at = CURRENT_TIMESTAMP
            RETURNING id
        """, (
            change_data.get("change_id"),
            change_data.get("change_number"),
            change_data.get("change_request", {}).get("requestor"),
            change_data.get("change_request", {}).get("request_date"),
            change_data.get("change_request", {}).get("change_type"),
            change_data.get("change_request", {}).get("change_reason"),
            change_data.get("change_request", {}).get("change_description"),
            change_data.get("change_request", {}).get("priority"),
            change_data.get("change_approval", {}).get("overall_status"),
            change_data.get("change_approval", {}).get("approval_date"),
            change_data.get("change_execution", {}).get("execution_status")
        ))
        self.conn.commit()
        return self.cur.fetchone()[0]

    def store_bom(self, bom_data: Dict) -> int:
        """存储BOM"""
        self.cur.execute("""
            INSERT INTO boms (
                bom_id, bom_number, product_id, bom_type,
                bom_version, bom_status, effective_date, expiry_date,
                creator, created_date
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (bom_id) DO UPDATE SET
                bom_version = EXCLUDED.bom_version,
                bom_status = EXCLUDED.bom_status
            RETURNING id
        """, (
            bom_data.get("bom_id"),
            bom_data.get("bom_number"),
            bom_data.get("product_id"),
            bom_data.get("bom_info", {}).get("bom_type"),
            bom_data.get("bom_info", {}).get("bom_version"),
            bom_data.get("bom_info", {}).get("bom_status"),
            bom_data.get("bom_info", {}).get("effective_date"),
            bom_data.get("bom_info", {}).get("expiry_date"),
            bom_data.get("bom_info", {}).get("creator"),
            bom_data.get("bom_info", {}).get("created_date")
        ))
        self.conn.commit()
        bom_id = self.cur.fetchone()[0]

        # 存储BOM项
        for item in bom_data.get("bom_structure", {}).get("bom_items", []):
            self.cur.execute("""
                INSERT INTO bom_items (
                    item_id, bom_id, material_id, material_name,
                    level, parent_item_id, quantity, unit, usage_type, sequence
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (item_id) DO UPDATE SET
                    quantity = EXCLUDED.quantity
            """, (
                item.get("item_id"),
                bom_data.get("bom_id"),
                item.get("material_id"),
                item.get("material_name"),
                item.get("level"),
                item.get("parent_item_id"),
                item.get("quantity"),
                item.get("unit"),
                item.get("usage_type"),
                item.get("sequence")
            ))
        self.conn.commit()

        return bom_id

    def close(self):
        """关闭数据库连接"""
        self.cur.close()
        self.conn.close()
```

### 5.2 PLM数据分析查询

**数据分析查询实现**：

```python
    def get_product_design_statistics(self, days: int = 30) -> Dict:
        """查询产品设计统计"""
        self.cur.execute("""
            SELECT
                COUNT(*) as total_products,
                COUNT(CASE WHEN design_status = 'Released' THEN 1 END) as released_products,
                COUNT(CASE WHEN design_stage = 'Production' THEN 1 END) as production_products,
                COUNT(DISTINCT designer) as total_designers
            FROM product_designs
            WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL '%s days'
        """, (days,))
        row = self.cur.fetchone()
        return {
            "total_products": row[0],
            "released_products": row[1],
            "production_products": row[2],
            "total_designers": row[3]
        }

    def get_change_statistics(self, days: int = 30) -> Dict:
        """查询变更统计"""
        self.cur.execute("""
            SELECT
                COUNT(*) as total_changes,
                COUNT(CASE WHEN overall_status = 'Approved' THEN 1 END) as approved_changes,
                COUNT(CASE WHEN execution_status = 'Completed' THEN 1 END) as completed_changes,
                COUNT(CASE WHEN priority = 'Urgent' THEN 1 END) as urgent_changes
            FROM change_management
            WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL '%s days'
        """, (days,))
        row = self.cur.fetchone()
        return {
            "total_changes": row[0],
            "approved_changes": row[1],
            "completed_changes": row[2],
            "urgent_changes": row[3]
        }

    def get_bom_statistics(self, product_id: str) -> Dict:
        """查询BOM统计"""
        self.cur.execute("""
            SELECT
                COUNT(DISTINCT bom_id) as total_boms,
                COUNT(DISTINCT material_id) as total_materials,
                MAX(level) as max_level,
                SUM(quantity) as total_quantity
            FROM bom_items
            WHERE bom_id IN (
                SELECT bom_id FROM boms WHERE product_id = %s
            )
        """, (product_id,))
        row = self.cur.fetchone()
        return {
            "total_boms": row[0],
            "total_materials": row[1],
            "max_level": row[2],
            "total_quantity": float(row[3]) if row[3] else None
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
