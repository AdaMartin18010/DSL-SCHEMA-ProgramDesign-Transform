# 建筑信息模型Schema转换体系

## 📑 目录

- [建筑信息模型Schema转换体系](#建筑信息模型schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
    - [1.1 转换目标](#11-转换目标)
  - [2. IFC文件解析实现](#2-ifc文件解析实现)
    - [2.1 IFC文件解析器](#21-ifc文件解析器)
    - [2.2 IFC实体解析器](#22-ifc实体解析器)
  - [3. gbXML处理实现](#3-gbxml处理实现)
    - [3.1 gbXML解析器](#31-gbxml解析器)
  - [4. COBie数据生成实现](#4-cobie数据生成实现)
    - [4.1 COBie数据生成器](#41-cobie数据生成器)
  - [5. CAD集成实现](#5-cad集成实现)
    - [5.1 CAD到IFC转换](#51-cad到ifc转换)
  - [6. BIM数据存储与分析](#6-bim数据存储与分析)
    - [6.1 PostgreSQL BIM数据存储](#61-postgresql-bim数据存储)

---

## 1. 转换体系概述

BIM Schema转换体系支持IFC文件、gbXML文件、COBie数据、
CAD文件、数据库存储之间的转换。

### 1.1 转换目标

1. **IFC文件解析**：IFC文件到数据库存储
2. **gbXML处理**：gbXML文件解析和生成
3. **COBie数据生成**：从IFC模型生成COBie数据
4. **CAD集成**：CAD文件与IFC文件之间的转换
5. **数据到数据库转换**：BIM数据到PostgreSQL存储

---

## 2. IFC文件解析实现

### 2.1 IFC文件解析器

**完整的IFC文件解析实现**：

```python
import logging
import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import os

logger = logging.getLogger(__name__)

class IFCParser:
    """IFC文件解析器 - 增强错误处理"""

    def __init__(self):
        self.header_pattern = re.compile(r'HEADER;')
        self.data_pattern = re.compile(r'DATA;')
        self.end_pattern = re.compile(r'ENDSEC;')
        # IFC实体模式：#<id>=<type>(<parameters>);
        self.entity_pattern = re.compile(r'#(\d+)\s*=\s*([A-Z_]+)\s*\(([^)]*)\);')
        # IFC引用模式：#<id>或$或*
        self.reference_pattern = re.compile(r'#(\d+)|(\$)|(\*)')

    def parse_ifc_file(self, file_path: str) -> Dict:
        """解析IFC文件 - 增强错误处理"""
        # 输入验证
        if not file_path:
            raise ValueError("IFC file path cannot be empty")

        if not isinstance(file_path, str):
            raise TypeError(f"IFC file path must be a string, got {type(file_path)}")

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"IFC file not found: {file_path}")

        if not os.path.isfile(file_path):
            raise ValueError(f"Path is not a file: {file_path}")

        # 检查文件扩展名
        if not file_path.lower().endswith(('.ifc', '.ifcxml', '.ifczip')):
            logger.warning(f"File extension is not .ifc, .ifcxml, or .ifczip: {file_path}")

        # 检查文件大小
        file_size = os.path.getsize(file_path)
        MAX_FILE_SIZE = 2 * 1024 * 1024 * 1024  # 2GB（IFC文件可能很大）
        if file_size > MAX_FILE_SIZE:
            raise ValueError(f"IFC file too large: {file_size} bytes (max {MAX_FILE_SIZE})")

        if file_size == 0:
            raise ValueError(f"IFC file is empty: {file_path}")

        try:
            # 检测文件编码
            encoding = self._detect_encoding(file_path)

            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()

            if not content.strip():
                raise ValueError(f"IFC file is empty or contains only whitespace: {file_path}")

            # 验证IFC文件格式
            if 'ISO-10303-21;' not in content and 'HEADER;' not in content:
                raise ValueError(f"Invalid IFC file: missing ISO-10303-21 header or HEADER section")

            if 'HEADER;' not in content:
                raise ValueError(f"Invalid IFC file: missing HEADER section")

            if 'DATA;' not in content:
                raise ValueError(f"Invalid IFC file: missing DATA section")

            # 解析文件结构
            header_end = content.find('ENDSEC;')
            if header_end == -1:
                raise ValueError(f"Invalid IFC file: missing ENDSEC in HEADER section")

            data_start = content.find('DATA;')
            if data_start == -1:
                raise ValueError(f"Invalid IFC file: missing DATA section")

            data_end = content.find('ENDSEC;', data_start)
            if data_end == -1:
                raise ValueError(f"Invalid IFC file: missing ENDSEC in DATA section")

            # 解析HEADER段
            header_section = content[:header_end + len('ENDSEC;')]
            header_data = self._parse_header(header_section)

            if not header_data:
                logger.warning(f"No header data parsed from IFC file: {file_path}")

            # 解析DATA段
            data_section = content[data_start:data_end + len('ENDSEC;')]
            entities = self._parse_data(data_section)

            if not entities:
                logger.warning(f"No entities parsed from IFC file: {file_path}")

            result = {
                "file_path": file_path,
                "file_size": file_size,
                "ifc_header": header_data,
                "ifc_data": {
                    "entities": entities,
                    "entity_count": len(entities)
                },
                "ifc_end": {
                    "end_marker": "END-ISO-10303-21;"
                }
            }

            logger.info(f"Successfully parsed IFC file: {file_path} ({len(entities)} entities)")
            return result

        except FileNotFoundError:
            raise
        except PermissionError as e:
            logger.error(f"Permission denied reading IFC file {file_path}: {e}")
            raise PermissionError(f"Cannot read IFC file: {e}") from e
        except UnicodeDecodeError as e:
            logger.error(f"Encoding error reading IFC file {file_path}: {e}")
            raise ValueError(f"Invalid file encoding: {e}") from e
        except ValueError as e:
            logger.error(f"Invalid IFC file format {file_path}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error parsing IFC file {file_path}: {e}", exc_info=True)
            raise RuntimeError(f"Failed to parse IFC file: {e}") from e

    def _detect_encoding(self, file_path: str) -> str:
        """检测文件编码"""
        import chardet

        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read(10000)  # 读取前10KB
                result = chardet.detect(raw_data)
                encoding = result.get('encoding', 'utf-8')

                # IFC文件通常使用ISO-8859-1或UTF-8
                if encoding and encoding.lower() in ['iso-8859-1', 'windows-1252']:
                    return 'iso-8859-1'
                return 'utf-8'
        except Exception:
            return 'utf-8'  # 默认使用UTF-8

    def _parse_header(self, header_section: str) -> Dict:
        """解析HEADER段"""
        header_data = {}

        try:
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
                header_data["preprocessor_version"] = parts[4] if len(parts) > 4 else ""
                header_data["originating_system"] = parts[5] if len(parts) > 5 else ""
                header_data["authorization"] = parts[6] if len(parts) > 6 else ""

            # 解析文件Schema
            file_schema_match = re.search(r'FILE_SCHEMA\s*\(([^)]+)\)', header_section)
            if file_schema_match:
                schema_content = file_schema_match.group(1)
                schemas = [s.strip().strip('"') for s in schema_content.split(',')]
                header_data["file_schema"] = schemas[0] if schemas else ""

            return header_data

        except Exception as e:
            logger.error(f"Error parsing IFC header: {e}")
            return {}

    def _parse_data(self, data_section: str) -> List[Dict]:
        """解析DATA段"""
        entities = []

        try:
            # 查找所有实体
            matches = self.entity_pattern.finditer(data_section)
            for match in matches:
                entity_id = int(match.group(1))
                entity_type = match.group(2)
                entity_params = match.group(3)

                # 解析参数
                params = self._parse_parameters(entity_params)

                entity = {
                    "id": entity_id,
                    "type": entity_type,
                    "parameters": params
                }

                entities.append(entity)

            return entities

        except Exception as e:
            logger.error(f"Error parsing IFC data section: {e}")
            return []

    def _parse_parameters(self, param_string: str) -> List:
        """解析实体参数"""
        params = []
        current_param = ""
        depth = 0
        in_string = False

        for char in param_string:
            if char == '"' and (not current_param or current_param[-1] != '\\'):
                in_string = not in_string
                current_param += char
            elif char == '(' and not in_string:
                depth += 1
                current_param += char
            elif char == ')' and not in_string:
                depth -= 1
                current_param += char
            elif char == ',' and depth == 0 and not in_string:
                params.append(self._parse_value(current_param.strip()))
                current_param = ""
            else:
                current_param += char

        if current_param.strip():
            params.append(self._parse_value(current_param.strip()))

        return params

    def _parse_value(self, value_str: str) -> any:
        """解析单个参数值"""
        value_str = value_str.strip()

        if not value_str or value_str == '$':
            return None

        if value_str == '*':
            return None

        # IFC引用
        if value_str.startswith('#'):
            return {"type": "reference", "id": int(value_str[1:])}

        # 字符串
        if value_str.startswith("'") and value_str.endswith("'"):
            return value_str[1:-1]

        # 数字
        try:
            if '.' in value_str:
                return float(value_str)
            return int(value_str)
        except ValueError:
            pass

        # 枚举值
        if value_str.startswith('.') and value_str.endswith('.'):
            return value_str[1:-1]

        return value_str
```

### 2.2 IFC实体解析器

**IFC实体解析器实现**：

```python
class IFCEntityParser:
    """IFC实体解析器 - 增强错误处理"""

    def __init__(self):
        self.entity_registry = {}  # 实体注册表

    def parse_ifc_wall(self, entity: Dict) -> Optional[Dict]:
        """解析IfcWall实体"""
        if not isinstance(entity, dict):
            raise TypeError(f"Entity must be a dictionary, got {type(entity)}")

        if entity.get("type") != "IFCWALL":
            raise ValueError(f"Entity type must be IFCWALL, got {entity.get('type')}")

        params = entity.get("parameters", [])
        if len(params) < 8:
            raise ValueError(f"IfcWall requires at least 8 parameters, got {len(params)}")

        try:
            wall_data = {
                "global_id": self._parse_guid(params[0]) if params[0] else None,
                "owner_history": self._parse_reference(params[1]) if params[1] else None,
                "name": self._parse_string(params[2]) if params[2] else None,
                "description": self._parse_string(params[3]) if params[3] else None,
                "object_type": self._parse_string(params[4]) if params[4] else None,
                "object_placement": self._parse_reference(params[5]) if params[5] else None,
                "representation": self._parse_reference(params[6]) if params[6] else None,
                "tag": self._parse_string(params[7]) if params[7] else None
            }

            return wall_data

        except Exception as e:
            logger.error(f"Error parsing IfcWall entity: {e}")
            raise ValueError(f"Failed to parse IfcWall: {e}") from e

    def parse_ifc_door(self, entity: Dict) -> Optional[Dict]:
        """解析IfcDoor实体"""
        if not isinstance(entity, dict):
            raise TypeError(f"Entity must be a dictionary, got {type(entity)}")

        if entity.get("type") != "IFCDOOR":
            raise ValueError(f"Entity type must be IFCDOOR, got {entity.get('type')}")

        params = entity.get("parameters", [])
        if len(params) < 8:
            raise ValueError(f"IfcDoor requires at least 8 parameters, got {len(params)}")

        try:
            door_data = {
                "global_id": self._parse_guid(params[0]) if params[0] else None,
                "owner_history": self._parse_reference(params[1]) if params[1] else None,
                "name": self._parse_string(params[2]) if params[2] else None,
                "description": self._parse_string(params[3]) if params[3] else None,
                "object_type": self._parse_string(params[4]) if params[4] else None,
                "object_placement": self._parse_reference(params[5]) if params[5] else None,
                "representation": self._parse_reference(params[6]) if params[6] else None,
                "tag": self._parse_string(params[7]) if params[7] else None,
                "overall_height": self._parse_real(params[8]) if len(params) > 8 and params[8] else None,
                "overall_width": self._parse_real(params[9]) if len(params) > 9 and params[9] else None
            }

            return door_data

        except Exception as e:
            logger.error(f"Error parsing IfcDoor entity: {e}")
            raise ValueError(f"Failed to parse IfcDoor: {e}") from e

    def parse_ifc_space(self, entity: Dict) -> Optional[Dict]:
        """解析IfcSpace实体"""
        if not isinstance(entity, dict):
            raise TypeError(f"Entity must be a dictionary, got {type(entity)}")

        if entity.get("type") != "IFCSPACE":
            raise ValueError(f"Entity type must be IFCSPACE, got {entity.get('type')}")

        params = entity.get("parameters", [])
        if len(params) < 8:
            raise ValueError(f"IfcSpace requires at least 8 parameters, got {len(params)}")

        try:
            space_data = {
                "global_id": self._parse_guid(params[0]) if params[0] else None,
                "owner_history": self._parse_reference(params[1]) if params[1] else None,
                "name": self._parse_string(params[2]) if params[2] else None,
                "description": self._parse_string(params[3]) if params[3] else None,
                "object_type": self._parse_string(params[4]) if params[4] else None,
                "object_placement": self._parse_reference(params[5]) if params[5] else None,
                "representation": self._parse_reference(params[6]) if params[6] else None,
                "long_name": self._parse_string(params[7]) if params[7] else None,
                "composition_type": self._parse_enum(params[8]) if len(params) > 8 and params[8] else None,
                "elevation_of_ref_height": self._parse_real(params[9]) if len(params) > 9 and params[9] else None,
                "elevation_of_terrain": self._parse_real(params[10]) if len(params) > 10 and params[10] else None,
                "building_storey": self._parse_reference(params[11]) if len(params) > 11 and params[11] else None
            }

            return space_data

        except Exception as e:
            logger.error(f"Error parsing IfcSpace entity: {e}")
            raise ValueError(f"Failed to parse IfcSpace: {e}") from e

    def _parse_guid(self, value: any) -> Optional[str]:
        """解析GUID值"""
        if value is None:
            return None

        if isinstance(value, str):
            # GUID格式：22个字符的字符串
            if len(value) == 22:
                return value
            elif value.startswith("'") and value.endswith("'"):
                guid = value[1:-1]
                if len(guid) == 22:
                    return guid

        raise ValueError(f"Invalid GUID format: {value}")

    def _parse_reference(self, value: any) -> Optional[Dict]:
        """解析引用值"""
        if value is None:
            return None

        if isinstance(value, dict) and value.get("type") == "reference":
            return value

        if isinstance(value, str) and value.startswith('#'):
            return {"type": "reference", "id": int(value[1:])}

        return None

    def _parse_string(self, value: any) -> Optional[str]:
        """解析字符串值"""
        if value is None:
            return None

        if isinstance(value, str):
            if value.startswith("'") and value.endswith("'"):
                return value[1:-1]
            return value

        return str(value)

    def _parse_real(self, value: any) -> Optional[float]:
        """解析实数值"""
        if value is None:
            return None

        if isinstance(value, (int, float)):
            return float(value)

        if isinstance(value, str):
            try:
                return float(value)
            except ValueError:
                return None

        return None

    def _parse_enum(self, value: any) -> Optional[str]:
        """解析枚举值"""
        if value is None:
            return None

        if isinstance(value, str):
            if value.startswith('.') and value.endswith('.'):
                return value[1:-1]
            return value

        return None
```

---

## 3. gbXML处理实现

### 3.1 gbXML解析器

**完整的gbXML解析实现**：

```python
import logging
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class gbXMLParser:
    """gbXML解析器 - 增强错误处理"""

    def __init__(self):
        self.namespaces = {
            'gbxml': 'http://www.gbxml.org/schema'
        }

    def parse_gbxml_file(self, file_path: str) -> Dict:
        """解析gbXML文件 - 增强错误处理"""
        # 输入验证
        if not file_path:
            raise ValueError("gbXML file path cannot be empty")

        if not isinstance(file_path, str):
            raise TypeError(f"gbXML file path must be a string, got {type(file_path)}")

        import os
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"gbXML file not found: {file_path}")

        if not os.path.isfile(file_path):
            raise ValueError(f"Path is not a file: {file_path}")

        # 检查文件扩展名
        if not file_path.lower().endswith('.xml'):
            logger.warning(f"File extension is not .xml: {file_path}")

        # 检查文件大小
        file_size = os.path.getsize(file_path)
        MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB
        if file_size > MAX_FILE_SIZE:
            raise ValueError(f"gbXML file too large: {file_size} bytes (max {MAX_FILE_SIZE})")

        if file_size == 0:
            raise ValueError(f"gbXML file is empty: {file_path}")

        try:
            # 解析XML文件
            tree = ET.parse(file_path)
            root = tree.getroot()

            # 验证根元素
            if root.tag not in ['{http://www.gbxml.org/schema}gbXML', 'gbXML']:
                raise ValueError(f"Invalid gbXML file: root element must be gbXML, got {root.tag}")

            # 解析gbXML结构
            gbxml_data = {
                "version": root.get("version", ""),
                "campus": self._parse_campus(root),
                "construction": self._parse_construction(root),
                "material": self._parse_material(root),
                "window_type": self._parse_window_type(root),
                "schedule": self._parse_schedule(root)
            }

            logger.info(f"Successfully parsed gbXML file: {file_path}")
            return gbxml_data

        except ET.ParseError as e:
            logger.error(f"XML parsing error in gbXML file {file_path}: {e}")
            raise ValueError(f"Invalid XML format: {e}") from e
        except FileNotFoundError:
            raise
        except PermissionError as e:
            logger.error(f"Permission denied reading gbXML file {file_path}: {e}")
            raise PermissionError(f"Cannot read gbXML file: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error parsing gbXML file {file_path}: {e}", exc_info=True)
            raise RuntimeError(f"Failed to parse gbXML file: {e}") from e

    def _parse_campus(self, root: ET.Element) -> Dict:
        """解析Campus元素"""
        campus_elem = root.find('.//{http://www.gbxml.org/schema}Campus')
        if campus_elem is None:
            campus_elem = root.find('.//Campus')

        if campus_elem is None:
            return {}

        campus_data = {
            "id": campus_elem.get("id", ""),
            "location": self._parse_location(campus_elem),
            "building": self._parse_building(campus_elem)
        }

        return campus_data

    def _parse_location(self, campus_elem: ET.Element) -> Dict:
        """解析Location元素"""
        location_elem = campus_elem.find('.//{http://www.gbxml.org/schema}Location')
        if location_elem is None:
            location_elem = campus_elem.find('.//Location')

        if location_elem is None:
            return {}

        location_data = {
            "latitude": float(location_elem.get("latitude", 0)),
            "longitude": float(location_elem.get("longitude", 0)),
            "elevation": float(location_elem.get("elevation", 0))
        }

        return location_data

    def _parse_building(self, campus_elem: ET.Element) -> Dict:
        """解析Building元素"""
        building_elem = campus_elem.find('.//{http://www.gbxml.org/schema}Building')
        if building_elem is None:
            building_elem = campus_elem.find('.//Building')

        if building_elem is None:
            return {}

        building_data = {
            "id": building_elem.get("id", ""),
            "building_type": building_elem.get("buildingType", ""),
            "spaces": self._parse_spaces(building_elem),
            "surfaces": self._parse_surfaces(building_elem)
        }

        return building_data

    def _parse_spaces(self, building_elem: ET.Element) -> List[Dict]:
        """解析Space元素列表"""
        spaces = []
        space_elems = building_elem.findall('.//{http://www.gbxml.org/schema}Space')
        if not space_elems:
            space_elems = building_elem.findall('.//Space')

        for space_elem in space_elems:
            space_data = {
                "id": space_elem.get("id", ""),
                "space_type": space_elem.get("spaceType", ""),
                "volume": float(space_elem.get("volume", 0)),
                "area": float(space_elem.get("area", 0)),
                "people_number": float(space_elem.get("peopleNumber", 0)),
                "lighting_power": float(space_elem.get("lightingPower", 0)),
                "equipment_power": float(space_elem.get("equipmentPower", 0))
            }
            spaces.append(space_data)

        return spaces

    def _parse_surfaces(self, building_elem: ET.Element) -> List[Dict]:
        """解析Surface元素列表"""
        surfaces = []
        surface_elems = building_elem.findall('.//{http://www.gbxml.org/schema}Surface')
        if not surface_elems:
            surface_elems = building_elem.findall('.//Surface')

        for surface_elem in surface_elems:
            surface_data = {
                "id": surface_elem.get("id", ""),
                "surface_type": surface_elem.get("surfaceType", ""),
                "construction_id_ref": surface_elem.get("constructionIdRef", ""),
                "planar_geometry": self._parse_planar_geometry(surface_elem)
            }
            surfaces.append(surface_data)

        return surfaces

    def _parse_planar_geometry(self, surface_elem: ET.Element) -> Dict:
        """解析PlanarGeometry元素"""
        geom_elem = surface_elem.find('.//{http://www.gbxml.org/schema}PlanarGeometry')
        if geom_elem is None:
            geom_elem = surface_elem.find('.//PlanarGeometry')

        if geom_elem is None:
            return {}

        polygon_elem = geom_elem.find('.//{http://www.gbxml.org/schema}Polygon')
        if polygon_elem is None:
            polygon_elem = geom_elem.find('.//Polygon')

        if polygon_elem is None:
            return {}

        loop_elem = polygon_elem.find('.//{http://www.gbxml.org/schema}Loop')
        if loop_elem is None:
            loop_elem = polygon_elem.find('.//Loop')

        if loop_elem is None:
            return {}

        cartesian_points = []
        point_elems = loop_elem.findall('.//{http://www.gbxml.org/schema}CartesianPoint')
        if not point_elems:
            point_elems = loop_elem.findall('.//CartesianPoint')

        for point_elem in point_elems:
            coord_elem = point_elem.find('.//{http://www.gbxml.org/schema}Coordinate')
            if coord_elem is None:
                coord_elem = point_elem.find('.//Coordinate')

            if coord_elem is not None:
                coords = [float(c.strip()) for c in coord_elem.text.split(',') if c.strip()]
                if len(coords) >= 3:
                    cartesian_points.append({
                        "x": coords[0],
                        "y": coords[1],
                        "z": coords[2]
                    })

        return {
            "polygon": {
                "points": cartesian_points
            }
        }

    def _parse_construction(self, root: ET.Element) -> List[Dict]:
        """解析Construction元素列表"""
        constructions = []
        constr_elems = root.findall('.//{http://www.gbxml.org/schema}Construction')
        if not constr_elems:
            constr_elems = root.findall('.//Construction')

        for constr_elem in constr_elems:
            constr_data = {
                "id": constr_elem.get("id", ""),
                "u_value": float(constr_elem.get("uValue", 0)),
                "layer_ids": [layer.get("layerIdRef", "")
                             for layer in constr_elem.findall('.//{http://www.gbxml.org/schema}Layer')]
            }
            constructions.append(constr_data)

        return constructions

    def _parse_material(self, root: ET.Element) -> List[Dict]:
        """解析Material元素列表"""
        materials = []
        mat_elems = root.findall('.//{http://www.gbxml.org/schema}Material')
        if not mat_elems:
            mat_elems = root.findall('.//Material')

        for mat_elem in mat_elems:
            mat_data = {
                "id": mat_elem.get("id", ""),
                "name": mat_elem.get("name", ""),
                "r_value": float(mat_elem.get("rValue", 0)),
                "thickness": float(mat_elem.get("thickness", 0)),
                "conductivity": float(mat_elem.get("conductivity", 0)),
                "density": float(mat_elem.get("density", 0)),
                "specific_heat": float(mat_elem.get("specificHeat", 0))
            }
            materials.append(mat_data)

        return materials

    def _parse_window_type(self, root: ET.Element) -> List[Dict]:
        """解析WindowType元素列表"""
        window_types = []
        wt_elems = root.findall('.//{http://www.gbxml.org/schema}WindowType')
        if not wt_elems:
            wt_elems = root.findall('.//WindowType')

        for wt_elem in wt_elems:
            wt_data = {
                "id": wt_elem.get("id", ""),
                "u_value": float(wt_elem.get("uValue", 0)),
                "shgc": float(wt_elem.get("shgc", 0)),
                "transmittance": float(wt_elem.get("transmittance", 0))
            }
            window_types.append(wt_data)

        return window_types

    def _parse_schedule(self, root: ET.Element) -> List[Dict]:
        """解析Schedule元素列表"""
        schedules = []
        sched_elems = root.findall('.//{http://www.gbxml.org/schema}Schedule')
        if not sched_elems:
            sched_elems = root.findall('.//Schedule')

        for sched_elem in sched_elems:
            sched_data = {
                "id": sched_elem.get("id", ""),
                "type": sched_elem.get("type", ""),
                "year_schedule": self._parse_year_schedule(sched_elem)
            }
            schedules.append(sched_data)

        return schedules

    def _parse_year_schedule(self, sched_elem: ET.Element) -> Dict:
        """解析YearSchedule元素"""
        ys_elem = sched_elem.find('.//{http://www.gbxml.org/schema}YearSchedule')
        if ys_elem is None:
            ys_elem = sched_elem.find('.//YearSchedule')

        if ys_elem is None:
            return {}

        return {
            "id": ys_elem.get("id", ""),
            "type": ys_elem.get("type", "")
        }
```

---

## 4. COBie数据生成实现

### 4.1 COBie数据生成器

**完整的COBie数据生成实现**：

```python
import logging
from typing import Dict, List, Optional
from datetime import datetime
import csv
import io

logger = logging.getLogger(__name__)

class COBieGenerator:
    """COBie数据生成器 - 增强错误处理"""

    def __init__(self):
        self.cobie_sheets = {
            "Contact": [],
            "Facility": [],
            "Floor": [],
            "Space": [],
            "Zone": [],
            "Type": [],
            "Component": [],
            "System": [],
            "Assembly": [],
            "Connection": [],
            "Spare": [],
            "Resource": [],
            "Job": [],
            "Impact": [],
            "Document": [],
            "Attribute": [],
            "Coordinate": [],
            "Issue": [],
            "Picklist": []
        }

    def generate_cobie_from_ifc(self, ifc_data: Dict) -> Dict:
        """从IFC数据生成COBie数据 - 增强错误处理"""
        if not isinstance(ifc_data, dict):
            raise TypeError(f"IFC data must be a dictionary, got {type(ifc_data)}")

        if "ifc_data" not in ifc_data:
            raise ValueError("IFC data missing 'ifc_data' section")

        entities = ifc_data.get("ifc_data", {}).get("entities", [])
        if not entities:
            raise ValueError("IFC data contains no entities")

        try:
            # 生成COBie各工作表
            self._generate_contact_sheet(ifc_data)
            self._generate_facility_sheet(ifc_data)
            self._generate_floor_sheet(ifc_data)
            self._generate_space_sheet(ifc_data)
            self._generate_type_sheet(ifc_data)
            self._generate_component_sheet(ifc_data)
            self._generate_system_sheet(ifc_data)

            cobie_data = {
                "version": "2.4",
                "generated_date": datetime.now().isoformat(),
                "sheets": self.cobie_sheets
            }

            logger.info("Successfully generated COBie data from IFC")
            return cobie_data

        except Exception as e:
            logger.error(f"Error generating COBie data: {e}", exc_info=True)
            raise RuntimeError(f"Failed to generate COBie data: {e}") from e

    def _generate_contact_sheet(self, ifc_data: Dict):
        """生成Contact工作表"""
        # 从IFC HEADER提取联系人信息
        header = ifc_data.get("ifc_header", {})

        contact = {
            "Email": header.get("file_author", ""),
            "CreatedBy": header.get("file_author", ""),
            "CreatedOn": datetime.now().isoformat(),
            "Category": "Owner"
        }

        self.cobie_sheets["Contact"].append(contact)

    def _generate_facility_sheet(self, ifc_data: Dict):
        """生成Facility工作表"""
        header = ifc_data.get("ifc_header", {})

        facility = {
            "Name": header.get("file_name", "Facility"),
            "CreatedBy": header.get("file_author", ""),
            "CreatedOn": datetime.now().isoformat(),
            "Category": "Building",
            "ProjectName": header.get("file_name", ""),
            "SiteName": "",
            "LinearUnits": "Meters",
            "AreaUnits": "SquareMeters",
            "VolumeUnits": "CubicMeters",
            "CurrencyUnit": "USD"
        }

        self.cobie_sheets["Facility"].append(facility)

    def _generate_floor_sheet(self, ifc_data: Dict):
        """生成Floor工作表"""
        entities = ifc_data.get("ifc_data", {}).get("entities", [])

        # 查找IfcBuildingStorey实体
        floors = {}
        for entity in entities:
            if entity.get("type") == "IFCBUILDINGSTOREY":
                floor_id = entity.get("id")
                params = entity.get("parameters", [])

                if params:
                    floor_name = self._get_string_value(params[2]) if len(params) > 2 else f"Floor_{floor_id}"
                    floors[floor_id] = {
                        "Name": floor_name,
                        "CreatedBy": "",
                        "CreatedOn": datetime.now().isoformat(),
                        "Category": "Floor",
                        "Elevation": self._get_real_value(params[5]) if len(params) > 5 else 0.0
                    }

        self.cobie_sheets["Floor"].extend(floors.values())

    def _generate_space_sheet(self, ifc_data: Dict):
        """生成Space工作表"""
        entities = ifc_data.get("ifc_data", {}).get("entities", [])

        # 查找IfcSpace实体
        spaces = {}
        for entity in entities:
            if entity.get("type") == "IFCSPACE":
                space_id = entity.get("id")
                params = entity.get("parameters", [])

                if params:
                    space_name = self._get_string_value(params[2]) if len(params) > 2 else f"Space_{space_id}"
                    spaces[space_id] = {
                        "Name": space_name,
                        "CreatedBy": "",
                        "CreatedOn": datetime.now().isoformat(),
                        "Category": "Space",
                        "FloorName": "",  # 需要关联到Floor
                        "Description": self._get_string_value(params[3]) if len(params) > 3 else "",
                        "GrossArea": 0.0,  # 需要从几何计算
                        "NetArea": 0.0
                    }

        self.cobie_sheets["Space"].extend(spaces.values())

    def _generate_type_sheet(self, ifc_data: Dict):
        """生成Type工作表"""
        entities = ifc_data.get("ifc_data", {}).get("entities", [])

        # 查找IfcTypeProduct实体
        types = {}
        for entity in entities:
            entity_type = entity.get("type")
            if entity_type and ("IFCTYPE" in entity_type or "IFCPRODUCT" in entity_type):
                type_id = entity.get("id")
                params = entity.get("parameters", [])

                if params:
                    type_name = self._get_string_value(params[2]) if len(params) > 2 else f"Type_{type_id}"
                    types[type_id] = {
                        "Name": type_name,
                        "CreatedBy": "",
                        "CreatedOn": datetime.now().isoformat(),
                        "Category": entity_type,
                        "Description": self._get_string_value(params[3]) if len(params) > 3 else "",
                        "Manufacturer": "",
                        "ModelNumber": "",
                        "WarrantyGuarantorParts": "",
                        "WarrantyDurationParts": "",
                        "ReplacementCost": 0.0
                    }

        self.cobie_sheets["Type"].extend(types.values())

    def _generate_component_sheet(self, ifc_data: Dict):
        """生成Component工作表"""
        entities = ifc_data.get("ifc_data", {}).get("entities", [])

        # 查找IfcProduct实体（墙、门、窗等）
        components = {}
        component_types = ["IFCWALL", "IFCDOOR", "IFCWINDOW", "IFCSLAB", "IFCCOLUMN", "IFCBEAM"]

        for entity in entities:
            entity_type = entity.get("type")
            if entity_type in component_types:
                comp_id = entity.get("id")
                params = entity.get("parameters", [])

                if params:
                    comp_name = self._get_string_value(params[2]) if len(params) > 2 else f"{entity_type}_{comp_id}"
                    components[comp_id] = {
                        "Name": comp_name,
                        "CreatedBy": "",
                        "CreatedOn": datetime.now().isoformat(),
                        "TypeName": "",  # 需要关联到Type
                        "Space": "",  # 需要关联到Space
                        "Description": self._get_string_value(params[3]) if len(params) > 3 else "",
                        "SerialNumber": "",
                        "InstallationDate": "",
                        "WarrantyStartDate": "",
                        "TagNumber": self._get_string_value(params[7]) if len(params) > 7 else "",
                        "BarCode": "",
                        "AssetIdentifier": ""
                    }

        self.cobie_sheets["Component"].extend(components.values())

    def _generate_system_sheet(self, ifc_data: Dict):
        """生成System工作表"""
        entities = ifc_data.get("ifc_data", {}).get("entities", [])

        # 查找IfcSystem实体（HVAC、电气、给排水等）
        systems = {}
        for entity in entities:
            entity_type = entity.get("type")
            if entity_type and "IFCSYSTEM" in entity_type:
                system_id = entity.get("id")
                params = entity.get("parameters", [])

                if params:
                    system_name = self._get_string_value(params[2]) if len(params) > 2 else f"System_{system_id}"
                    systems[system_id] = {
                        "Name": system_name,
                        "CreatedBy": "",
                        "CreatedOn": datetime.now().isoformat(),
                        "Category": entity_type,
                        "ComponentNames": ""  # 需要关联到Component
                    }

        self.cobie_sheets["System"].extend(systems.values())

    def export_to_csv(self, cobie_data: Dict, output_dir: str) -> List[str]:
        """导出COBie数据到CSV文件"""
        if not isinstance(cobie_data, dict):
            raise TypeError(f"COBie data must be a dictionary, got {type(cobie_data)}")

        if "sheets" not in cobie_data:
            raise ValueError("COBie data missing 'sheets' section")

        import os
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        exported_files = []

        try:
            sheets = cobie_data.get("sheets", {})
            for sheet_name, sheet_data in sheets.items():
                if not sheet_data:
                    continue

                csv_file_path = os.path.join(output_dir, f"{sheet_name}.csv")

                with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
                    if sheet_data:
                        fieldnames = sheet_data[0].keys()
                        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                        writer.writeheader()
                        writer.writerows(sheet_data)

                exported_files.append(csv_file_path)
                logger.info(f"Exported {sheet_name} sheet to {csv_file_path}")

            return exported_files

        except Exception as e:
            logger.error(f"Error exporting COBie data to CSV: {e}", exc_info=True)
            raise RuntimeError(f"Failed to export COBie data: {e}") from e

    def _get_string_value(self, value: any) -> str:
        """获取字符串值"""
        if value is None:
            return ""

        if isinstance(value, str):
            if value.startswith("'") and value.endswith("'"):
                return value[1:-1]
            return value

        return str(value)

    def _get_real_value(self, value: any) -> float:
        """获取实数值"""
        if value is None:
            return 0.0

        if isinstance(value, (int, float)):
            return float(value)

        if isinstance(value, str):
            try:
                return float(value)
            except ValueError:
                return 0.0

        return 0.0
```

---

## 5. CAD集成实现

### 5.1 CAD到IFC转换

**CAD到IFC转换器实现**：

```python
class CADToIFCConverter:
    """CAD到IFC转换器 - 增强错误处理"""

    def __init__(self):
        pass

    def convert_cad_to_ifc(self, cad_file_path: str, output_ifc_path: str) -> bool:
        """将CAD文件转换为IFC文件"""
        if not cad_file_path:
            raise ValueError("CAD file path cannot be empty")

        if not isinstance(cad_file_path, str):
            raise TypeError(f"CAD file path must be a string, got {type(cad_file_path)}")

        if not output_ifc_path:
            raise ValueError("Output IFC file path cannot be empty")

        import os
        if not os.path.exists(cad_file_path):
            raise FileNotFoundError(f"CAD file not found: {cad_file_path}")

        try:
            # 实际实现需要使用CAD库（如FreeCAD、IfcOpenShell等）
            # 这里提供框架代码

            # 1. 读取CAD文件
            cad_data = self._read_cad_file(cad_file_path)

            # 2. 转换为IFC实体
            ifc_entities = self._convert_cad_to_ifc_entities(cad_data)

            # 3. 生成IFC文件
            self._write_ifc_file(ifc_entities, output_ifc_path)

            logger.info(f"Successfully converted CAD file {cad_file_path} to IFC file {output_ifc_path}")
            return True

        except Exception as e:
            logger.error(f"Error converting CAD to IFC: {e}", exc_info=True)
            raise RuntimeError(f"Failed to convert CAD to IFC: {e}") from e

    def _read_cad_file(self, cad_file_path: str) -> Dict:
        """读取CAD文件（模拟实现）"""
        # 实际实现需要使用CAD库
        return {}

    def _convert_cad_to_ifc_entities(self, cad_data: Dict) -> List[Dict]:
        """将CAD数据转换为IFC实体（模拟实现）"""
        # 实际实现需要根据CAD数据生成IFC实体
        return []

    def _write_ifc_file(self, entities: List[Dict], output_path: str):
        """写入IFC文件"""
        try:
            with open(output_path, 'w', encoding='iso-8859-1') as f:
                # 写入IFC文件头
                f.write("ISO-10303-21;\n")
                f.write("HEADER;\n")
                f.write("FILE_DESCRIPTION(('IFC4'),'2;1');\n")
                f.write("FILE_NAME('converted.ifc','2025-01-21T00:00:00',(''),(''),'CAD Converter','','');\n")
                f.write("FILE_SCHEMA(('IFC4'));\n")
                f.write("ENDSEC;\n")

                # 写入DATA段
                f.write("DATA;\n")
                for entity in entities:
                    f.write(f"#{entity['id']}={entity['type']}({','.join(str(p) for p in entity['parameters'])});\n")
                f.write("ENDSEC;\n")

                f.write("END-ISO-10303-21;\n")

        except Exception as e:
            logger.error(f"Error writing IFC file: {e}")
            raise
```

---

## 6. BIM数据存储与分析

### 6.1 PostgreSQL BIM数据存储

**完整的PostgreSQL存储实现**：

```python
import logging
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class BIMStorage:
    """BIM数据存储 - 增强错误处理"""

    def __init__(self, db_config: Dict):
        if not isinstance(db_config, dict):
            raise TypeError(f"Database config must be a dictionary, got {type(db_config)}")

        required_fields = ["host", "port", "database", "user", "password"]
        missing_fields = [f for f in required_fields if f not in db_config]
        if missing_fields:
            raise ValueError(f"Missing required database config fields: {', '.join(missing_fields)}")

        self.db_config = db_config
        self.conn: Optional[psycopg2.extensions.connection] = None

    def connect(self):
        """连接数据库"""
        try:
            self.conn = psycopg2.connect(
                host=self.db_config["host"],
                port=self.db_config["port"],
                database=self.db_config["database"],
                user=self.db_config["user"],
                password=self.db_config["password"]
            )
            logger.info("Connected to PostgreSQL database")
        except psycopg2.Error as e:
            logger.error(f"Failed to connect to database: {e}")
            raise ConnectionError(f"Failed to connect to database: {e}") from e

    def create_tables(self):
        """创建表结构"""
        if self.conn is None:
            raise ConnectionError("Database not connected. Call connect() first.")

        try:
            with self.conn.cursor() as cur:
                # IFC文件表
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS ifc_files (
                        id SERIAL PRIMARY KEY,
                        file_path VARCHAR(500) NOT NULL,
                        file_name VARCHAR(255) NOT NULL,
                        file_size BIGINT NOT NULL CHECK (file_size >= 0),
                        file_schema VARCHAR(100),
                        file_author VARCHAR(255),
                        entity_count INTEGER NOT NULL CHECK (entity_count >= 0),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # IFC实体表
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS ifc_entities (
                        id SERIAL PRIMARY KEY,
                        ifc_file_id INTEGER REFERENCES ifc_files(id) ON DELETE CASCADE,
                        entity_id INTEGER NOT NULL,
                        entity_type VARCHAR(100) NOT NULL,
                        global_id VARCHAR(255),
                        name VARCHAR(255),
                        description TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # 建筑元素表
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS building_elements (
                        id SERIAL PRIMARY KEY,
                        entity_id INTEGER REFERENCES ifc_entities(id) ON DELETE CASCADE,
                        element_type VARCHAR(50) NOT NULL,
                        tag VARCHAR(100),
                        material VARCHAR(255),
                        dimensions JSONB,
                        location JSONB,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # 空间表
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS spaces (
                        id SERIAL PRIMARY KEY,
                        entity_id INTEGER REFERENCES ifc_entities(id) ON DELETE CASCADE,
                        space_name VARCHAR(255) NOT NULL,
                        space_type VARCHAR(100),
                        floor_name VARCHAR(255),
                        area DECIMAL(10,2) CHECK (area >= 0),
                        volume DECIMAL(10,2) CHECK (volume >= 0),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # COBie数据表
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS cobie_data (
                        id SERIAL PRIMARY KEY,
                        sheet_name VARCHAR(50) NOT NULL,
                        row_data JSONB NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # 创建索引
                cur.execute("CREATE INDEX IF NOT EXISTS idx_ifc_file_path ON ifc_files(file_path)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_ifc_entity_type ON ifc_entities(entity_type)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_ifc_entity_global_id ON ifc_entities(global_id)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_building_element_type ON building_elements(element_type)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_space_name ON spaces(space_name)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_cobie_sheet ON cobie_data(sheet_name)")

                self.conn.commit()
                logger.info("Created BIM database tables")

        except psycopg2.Error as e:
            logger.error(f"Failed to create tables: {e}")
            self.conn.rollback()
            raise RuntimeError(f"Failed to create tables: {e}") from e

    def store_ifc_file(self, ifc_data: Dict) -> int:
        """存储IFC文件信息"""
        if self.conn is None:
            raise ConnectionError("Database not connected. Call connect() first.")

        if not isinstance(ifc_data, dict):
            raise TypeError(f"IFC data must be a dictionary, got {type(ifc_data)}")

        required_fields = ["file_path", "file_size", "entity_count"]
        missing_fields = [f for f in required_fields if f not in ifc_data]
        if missing_fields:
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")

        try:
            header = ifc_data.get("ifc_header", {})

            with self.conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO ifc_files
                    (file_path, file_name, file_size, file_schema, file_author, entity_count)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    ifc_data["file_path"],
                    header.get("file_name", ""),
                    ifc_data["file_size"],
                    header.get("file_schema", ""),
                    header.get("file_author", ""),
                    ifc_data["entity_count"]
                ))

                file_id = cur.fetchone()[0]
                self.conn.commit()

                # 存储实体
                entities = ifc_data.get("ifc_data", {}).get("entities", [])
                for entity in entities:
                    self._store_ifc_entity(file_id, entity)

                logger.info(f"Stored IFC file with ID: {file_id}")
                return file_id

        except psycopg2.Error as e:
            logger.error(f"Failed to store IFC file: {e}")
            self.conn.rollback()
            raise RuntimeError(f"Failed to store IFC file: {e}") from e

    def _store_ifc_entity(self, file_id: int, entity: Dict):
        """存储IFC实体"""
        try:
            params = entity.get("parameters", [])

            with self.conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO ifc_entities
                    (ifc_file_id, entity_id, entity_type, global_id, name, description)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    file_id,
                    entity.get("id"),
                    entity.get("type"),
                    self._get_guid_from_params(params) if params else None,
                    self._get_string_from_params(params, 2) if len(params) > 2 else None,
                    self._get_string_from_params(params, 3) if len(params) > 3 else None
                ))

        except psycopg2.Error as e:
            logger.error(f"Failed to store IFC entity: {e}")
            raise

    def _get_guid_from_params(self, params: List) -> Optional[str]:
        """从参数中提取GUID"""
        if params and params[0]:
            value = params[0]
            if isinstance(value, str) and len(value) == 22:
                return value
        return None

    def _get_string_from_params(self, params: List, index: int) -> Optional[str]:
        """从参数中提取字符串"""
        if index < len(params) and params[index]:
            value = params[index]
            if isinstance(value, str):
                if value.startswith("'") and value.endswith("'"):
                    return value[1:-1]
                return value
        return None

    def query_building_elements(self, element_type: str = None) -> List[Dict]:
        """查询建筑元素"""
        if self.conn is None:
            raise ConnectionError("Database not connected. Call connect() first.")

        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                if element_type:
                    cur.execute("""
                        SELECT * FROM building_elements
                        WHERE element_type = %s
                        ORDER BY created_at DESC
                    """, (element_type,))
                else:
                    cur.execute("""
                        SELECT * FROM building_elements
                        ORDER BY created_at DESC
                    """)

                return cur.fetchall()

        except psycopg2.Error as e:
            logger.error(f"Failed to query building elements: {e}")
            raise RuntimeError(f"Failed to query building elements: {e}") from e
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21
