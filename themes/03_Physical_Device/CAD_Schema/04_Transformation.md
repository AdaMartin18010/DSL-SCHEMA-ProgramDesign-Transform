# CAD Schema转换体系

## 📑 目录

- [CAD Schema转换体系](#cad-schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
    - [1.1 转换目标](#11-转换目标)
  - [2. CAD格式转换](#2-cad格式转换)
    - [2.1 STEP格式转换](#21-step格式转换)
    - [2.2 IGES格式转换](#22-iges格式转换)
    - [2.3 原生CAD格式转换](#23-原生cad格式转换)
  - [3. 几何模型转换](#3-几何模型转换)
  - [4. 结构设计转换](#4-结构设计转换)
  - [5. 机构设计转换](#5-机构设计转换)
  - [6. 转换工具](#6-转换工具)
  - [7. 转换验证](#7-转换验证)
  - [8. CAD数据存储与分析](#8-cad数据存储与分析)
    - [8.1 PostgreSQL CAD数据存储](#81-postgresql-cad数据存储)
    - [8.2 CAD数据分析查询](#82-cad数据分析查询)

---

## 1. 转换体系概述

CAD Schema转换体系支持不同CAD格式之间的转换，
以及CAD数据到其他格式的转换。

### 1.1 转换目标

1. **格式转换**：STEP ↔ IGES ↔ 原生CAD格式
2. **几何转换**：几何模型格式转换
3. **结构转换**：结构设计数据转换
4. **机构转换**：机构设计数据转换

---

## 2. CAD格式转换

### 2.1 STEP格式转换

**转换规则**：

- STEP AP 203 → STEP AP 242
- STEP AP 214 → STEP AP 242
- STEP几何 → 其他CAD格式几何

### 2.2 IGES格式转换

**转换规则**：

- IGES → STEP
- IGES几何 → 其他格式几何

### 2.3 原生CAD格式转换

**转换规则**：

- SolidWorks → STEP
- CATIA → STEP
- AutoCAD → STEP
- FreeCAD → STEP

---

## 3. 几何模型转换

支持NURBS、B样条、B-rep、CSG等几何表示之间的转换。

---

## 4. 结构设计转换

支持结构设计数据到有限元分析软件的转换。

---

## 5. 机构设计转换

支持机构设计数据到运动仿真软件的转换。

---

## 6. 转换工具

- **OpenCASCADE**：开源CAD内核
- **FreeCAD**：开源CAD软件
- **CAD Exchanger**：CAD格式转换工具

---

## 7. 转换验证

验证转换的几何完整性、数据完整性和语义等价性。

---

## 8. CAD数据存储与分析

### 8.1 PostgreSQL CAD数据存储

**CAD数据存储方案**：

```python
import psycopg2
import json
from typing import Dict, List, Optional
from datetime import datetime

class CADStorage:
    """CAD数据存储系统"""

    def __init__(self, connection_string: str):
        self.conn = psycopg2.connect(connection_string)
        self.cur = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        """创建CAD数据表"""
        # 几何模型表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS geometry_models (
                id SERIAL PRIMARY KEY,
                model_name VARCHAR(200) UNIQUE NOT NULL,
                model_type VARCHAR(50) NOT NULL,
                geometry_data JSONB NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 结构设计表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS structural_designs (
                id SERIAL PRIMARY KEY,
                design_name VARCHAR(200) UNIQUE NOT NULL,
                geometry_id INTEGER NOT NULL,
                material_data JSONB NOT NULL,
                loads_data JSONB,
                boundary_conditions JSONB,
                fea_model JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (geometry_id) REFERENCES geometry_models(id)
            )
        """)

        # 机构设计表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS mechanism_designs (
                id SERIAL PRIMARY KEY,
                mechanism_name VARCHAR(200) UNIQUE NOT NULL,
                joints_data JSONB NOT NULL,
                links_data JSONB NOT NULL,
                kinematics_data JSONB,
                dynamics_data JSONB,
                degrees_of_freedom INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 装配表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS assemblies (
                id SERIAL PRIMARY KEY,
                assembly_name VARCHAR(200) UNIQUE NOT NULL,
                parts_data JSONB NOT NULL,
                relationships JSONB NOT NULL,
                constraints JSONB NOT NULL,
                hierarchy JSONB NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 工程图表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS engineering_drawings (
                id SERIAL PRIMARY KEY,
                drawing_number VARCHAR(100) UNIQUE NOT NULL,
                title VARCHAR(500),
                views_data JSONB NOT NULL,
                annotations JSONB,
                pmi_data JSONB,
                layers JSONB,
                title_block JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # CAD文件版本表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS cad_file_versions (
                id SERIAL PRIMARY KEY,
                file_name VARCHAR(500) NOT NULL,
                version_number VARCHAR(50) NOT NULL,
                file_format VARCHAR(50) NOT NULL,
                file_path TEXT,
                file_size BIGINT,
                checksum VARCHAR(64),
                metadata JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(file_name, version_number)
            )
        """)

        # 创建索引
        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_geometry_model_type
            ON geometry_models(model_type)
        """)
        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_drawing_number
            ON engineering_drawings(drawing_number)
        """)

        self.conn.commit()

    def store_geometry_model(self, model_name: str, model_type: str,
                            geometry_data: Dict):
        """存储几何模型"""
        self.cur.execute("""
            INSERT INTO geometry_models
            (model_name, model_type, geometry_data)
            VALUES (%s, %s, %s::jsonb)
            ON CONFLICT (model_name) DO UPDATE
            SET model_type = EXCLUDED.model_type,
                geometry_data = EXCLUDED.geometry_data,
                updated_at = CURRENT_TIMESTAMP
        """, (model_name, model_type, json.dumps(geometry_data)))
        self.conn.commit()

    def store_structural_design(self, design_name: str, geometry_id: int,
                                material_data: Dict, loads_data: Dict = None,
                                boundary_conditions: Dict = None,
                                fea_model: Dict = None):
        """存储结构设计"""
        self.cur.execute("""
            INSERT INTO structural_designs
            (design_name, geometry_id, material_data, loads_data,
             boundary_conditions, fea_model)
            VALUES (%s, %s, %s::jsonb, %s::jsonb, %s::jsonb, %s::jsonb)
            ON CONFLICT (design_name) DO UPDATE
            SET geometry_id = EXCLUDED.geometry_id,
                material_data = EXCLUDED.material_data,
                loads_data = EXCLUDED.loads_data,
                boundary_conditions = EXCLUDED.boundary_conditions,
                fea_model = EXCLUDED.fea_model
        """, (design_name, geometry_id, json.dumps(material_data),
              json.dumps(loads_data or {}),
              json.dumps(boundary_conditions or {}),
              json.dumps(fea_model or {})))
        self.conn.commit()

    def store_mechanism_design(self, mechanism_name: str,
                               joints_data: Dict, links_data: Dict,
                               kinematics_data: Dict = None,
                               dynamics_data: Dict = None,
                               degrees_of_freedom: int = None):
        """存储机构设计"""
        self.cur.execute("""
            INSERT INTO mechanism_designs
            (mechanism_name, joints_data, links_data, kinematics_data,
             dynamics_data, degrees_of_freedom)
            VALUES (%s, %s::jsonb, %s::jsonb, %s::jsonb, %s::jsonb, %s)
            ON CONFLICT (mechanism_name) DO UPDATE
            SET joints_data = EXCLUDED.joints_data,
                links_data = EXCLUDED.links_data,
                kinematics_data = EXCLUDED.kinematics_data,
                dynamics_data = EXCLUDED.dynamics_data,
                degrees_of_freedom = EXCLUDED.degrees_of_freedom
        """, (mechanism_name, json.dumps(joints_data),
              json.dumps(links_data),
              json.dumps(kinematics_data or {}),
              json.dumps(dynamics_data or {}),
              degrees_of_freedom))
        self.conn.commit()

    def store_assembly(self, assembly_name: str, parts_data: Dict,
                      relationships: Dict, constraints: Dict,
                      hierarchy: Dict):
        """存储装配"""
        self.cur.execute("""
            INSERT INTO assemblies
            (assembly_name, parts_data, relationships, constraints, hierarchy)
            VALUES (%s, %s::jsonb, %s::jsonb, %s::jsonb, %s::jsonb)
            ON CONFLICT (assembly_name) DO UPDATE
            SET parts_data = EXCLUDED.parts_data,
                relationships = EXCLUDED.relationships,
                constraints = EXCLUDED.constraints,
                hierarchy = EXCLUDED.hierarchy
        """, (assembly_name, json.dumps(parts_data),
              json.dumps(relationships), json.dumps(constraints),
              json.dumps(hierarchy)))
        self.conn.commit()

    def store_engineering_drawing(self, drawing_number: str, title: str,
                                 views_data: Dict, annotations: Dict = None,
                                 pmi_data: Dict = None, layers: Dict = None,
                                 title_block: Dict = None):
        """存储工程图"""
        self.cur.execute("""
            INSERT INTO engineering_drawings
            (drawing_number, title, views_data, annotations, pmi_data,
             layers, title_block)
            VALUES (%s, %s, %s::jsonb, %s::jsonb, %s::jsonb, %s::jsonb, %s::jsonb)
            ON CONFLICT (drawing_number) DO UPDATE
            SET title = EXCLUDED.title,
                views_data = EXCLUDED.views_data,
                annotations = EXCLUDED.annotations,
                pmi_data = EXCLUDED.pmi_data,
                layers = EXCLUDED.layers,
                title_block = EXCLUDED.title_block
        """, (drawing_number, title, json.dumps(views_data),
              json.dumps(annotations or {}), json.dumps(pmi_data or {}),
              json.dumps(layers or {}), json.dumps(title_block or {})))
        self.conn.commit()

    def store_cad_file_version(self, file_name: str, version_number: str,
                               file_format: str, file_path: str = None,
                               file_size: int = None, checksum: str = None,
                               metadata: Dict = None):
        """存储CAD文件版本"""
        self.cur.execute("""
            INSERT INTO cad_file_versions
            (file_name, version_number, file_format, file_path, file_size,
             checksum, metadata)
            VALUES (%s, %s, %s, %s, %s, %s, %s::jsonb)
            ON CONFLICT (file_name, version_number) DO UPDATE
            SET file_format = EXCLUDED.file_format,
                file_path = EXCLUDED.file_path,
                file_size = EXCLUDED.file_size,
                checksum = EXCLUDED.checksum,
                metadata = EXCLUDED.metadata
        """, (file_name, version_number, file_format, file_path,
              file_size, checksum, json.dumps(metadata or {})))
        self.conn.commit()
```

### 8.2 CAD数据分析查询

**查询示例**：

```python
# 查询几何模型
storage.cur.execute("""
    SELECT model_name, model_type, geometry_data
    FROM geometry_models
    WHERE model_type = %s
""", ("BRepSolid",))

# 查询结构设计
storage.cur.execute("""
    SELECT design_name, material_data, fea_model
    FROM structural_designs
    WHERE geometry_id = %s
""", (geometry_id,))

# 查询机构设计
storage.cur.execute("""
    SELECT mechanism_name, degrees_of_freedom, kinematics_data
    FROM mechanism_designs
    WHERE degrees_of_freedom = %s
""", (dof,))
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21
