# 建筑信息模型Schema实践案例

## 📑 目录

- [建筑信息模型Schema实践案例](#建筑信息模型schema实践案例)
  - [📑 目录](#-目录)
  - [1. 案例概述](#1-案例概述)
  - [2. 案例1：建筑设计管理](#2-案例1建筑设计管理)
    - [2.1 场景描述](#21-场景描述)
    - [2.2 Schema定义](#22-schema定义)
    - [2.3 实现代码](#23-实现代码)
  - [3. 案例2：IFC文件解析和存储](#3-案例2ifc文件解析和存储)
    - [3.1 场景描述](#31-场景描述)
    - [3.2 Schema定义](#32-schema定义)
    - [3.3 实现代码](#33-实现代码)
  - [4. 案例3：施工管理](#4-案例3施工管理)
    - [4.1 场景描述](#41-场景描述)
    - [4.2 Schema定义](#42-schema定义)
    - [4.3 实现代码](#43-实现代码)
  - [5. 案例4：COBie数据生成](#5-案例4cobie数据生成)
    - [5.1 场景描述](#51-场景描述)
    - [5.2 Schema定义](#52-schema定义)
    - [5.3 实现代码](#53-实现代码)
  - [6. 案例5：gbXML能耗分析](#6-案例5gbxml能耗分析)
    - [6.1 场景描述](#61-场景描述)
    - [6.2 Schema定义](#62-schema定义)
    - [6.3 实现代码](#63-实现代码)
  - [7. 案例6：运维管理](#7-案例6运维管理)
    - [7.1 场景描述](#71-场景描述)
    - [7.2 Schema定义](#72-schema定义)
    - [7.3 实现代码](#73-实现代码)
  - [8. 案例7：BIM数据查询和分析](#8-案例7bim数据查询和分析)
    - [8.1 场景描述](#81-场景描述)
    - [8.2 实现代码](#82-实现代码)
  - [9. 案例8：智能建筑运营系统](#9-案例8智能建筑运营系统)
    - [9.1 场景描述](#91-场景描述)
    - [9.2 Schema定义](#92-schema定义)
    - [9.3 实现代码](#93-实现代码)
  - [10. 案例9：建筑能耗优化系统](#10-案例9建筑能耗优化系统)
    - [10.1 场景描述](#101-场景描述)
    - [10.2 Schema定义](#102-schema定义)
    - [10.3 实现代码](#103-实现代码)
  - [11. 案例10：建筑维护管理系统](#11-案例10建筑维护管理系统)
    - [11.1 场景描述](#111-场景描述)
    - [11.2 Schema定义](#112-schema定义)
    - [11.3 实现代码](#113-实现代码)

---

## 1. 案例概述

本文档提供建筑信息模型Schema在实际应用中的实践案例，涵盖建筑设计、IFC文件处理、施工管理、COBie数据生成、gbXML能耗分析、运维管理等场景。

---

## 2. 案例1：建筑设计管理

### 2.1 场景描述

**业务背景**：
建筑设计公司需要管理建筑项目的设计数据，包括建筑元素、空间定义、材料属性等，确保设计数据的一致性和可追溯性。

**技术挑战**：

- 需要管理多种建筑元素类型（墙、柱、梁、板、门、窗等）
- 需要定义空间关系（楼层、房间、区域）
- 需要管理材料属性和几何信息
- 需要支持IFC标准数据格式

**解决方案**：
使用BIM_Schema定义建筑设计数据结构，实现建筑元素的创建、空间的定义、材料的管理等功能。

### 2.2 Schema定义

**建筑设计管理Schema**：

```json
{
  "project_id": "PROJ20250121001",
  "project_name": "办公楼A",
  "building_elements": [
    {
      "element_id": "ELEM001",
      "element_type": "Wall",
      "global_id": "3xK8j9L2mN4pQ6rS8tU0vW",
      "name": "外墙-东侧",
      "description": "钢筋混凝土外墙",
      "tag": "W-001",
      "geometry": {
        "placement": {
          "location": {
            "x": 0.0,
            "y": 0.0,
            "z": 0.0
          },
          "axis": {
            "x": 0.0,
            "y": 1.0,
            "z": 0.0
          }
        },
        "representation": {
          "representation_type": "SweptSolid",
          "shape": {
            "dimensions": {
              "length": 20.0,
              "height": 3.0,
              "thickness": 0.3
            },
            "volume": 18.0,
            "area": 60.0
          }
        }
      },
      "material": {
        "material_id": "MAT001",
        "material_name": "C30混凝土",
        "material_type": "Concrete",
        "properties": {
          "density": 2400.0,
          "thermal_conductivity": 1.51,
          "specific_heat": 920.0,
          "strength": 30.0
        }
      }
    },
    {
      "element_id": "ELEM002",
      "element_type": "Door",
      "global_id": "4yL9k0M3nO5qR7sT9uV1wX",
      "name": "主入口门",
      "description": "双扇玻璃门",
      "tag": "D-001",
      "geometry": {
        "placement": {
          "location": {
            "x": 10.0,
            "y": 0.0,
            "z": 0.0
          }
        },
        "representation": {
          "representation_type": "BRep",
          "shape": {
            "dimensions": {
              "width": 2.0,
              "height": 2.5,
              "thickness": 0.1
            },
            "area": 5.0
          }
        }
      }
    }
  ],
  "spaces": [
    {
      "space_id": "SPACE001",
      "global_id": "5zM0l1N4oP6rS8tU0vW2xY",
      "space_name": "办公室101",
      "space_type": "Room",
      "long_name": "一层办公室101",
      "description": "标准办公室",
      "geometry": {
        "placement": {
          "location": {
            "x": 5.0,
            "y": 5.0,
            "z": 0.0
          }
        },
        "representation": {
          "representation_type": "BRep",
          "shape": {
            "volume": 60.0,
            "area": 20.0
          }
        }
      },
      "floor": "F1",
      "elevation": 0.0,
      "height": 3.0
    }
  ],
  "floors": [
    {
      "floor_id": "FLOOR001",
      "global_id": "6aN1m2O5pQ7sT9uV1wX3yZ",
      "floor_name": "一层",
      "elevation": 0.0,
      "height": 3.0
    }
  ]
}
```

### 2.3 实现代码

**完整的建筑设计管理实现**：

```python
import logging
from typing import Dict, List
from datetime import datetime
from bim_schema.transformation import BIMStorage

logger = logging.getLogger(__name__)

# 案例1：建筑设计管理
def case1_building_design_management():
    """案例1：建筑设计管理"""

    # 1. 初始化BIM存储
    db_config = {
        "host": "localhost",
        "port": 5432,
        "database": "bim_db",
        "user": "bim_user",
        "password": "bim_password"
    }
    storage = BIMStorage(db_config)
    storage.connect()
    storage.create_tables()

    # 2. 创建建筑项目
    project_data = {
        "project_id": "PROJ20250121001",
        "project_name": "办公楼A",
        "building_elements": [
            {
                "element_id": "ELEM001",
                "element_type": "Wall",
                "global_id": "3xK8j9L2mN4pQ6rS8tU0vW",
                "name": "外墙-东侧",
                "description": "钢筋混凝土外墙",
                "tag": "W-001",
                "geometry": {
                    "placement": {
                        "location": {"x": 0.0, "y": 0.0, "z": 0.0},
                        "axis": {"x": 0.0, "y": 1.0, "z": 0.0}
                    },
                    "representation": {
                        "representation_type": "SweptSolid",
                        "shape": {
                            "dimensions": {
                                "length": 20.0,
                                "height": 3.0,
                                "thickness": 0.3
                            },
                            "volume": 18.0,
                            "area": 60.0
                        }
                    }
                },
                "material": {
                    "material_id": "MAT001",
                    "material_name": "C30混凝土",
                    "material_type": "Concrete",
                    "properties": {
                        "density": 2400.0,
                        "thermal_conductivity": 1.51,
                        "specific_heat": 920.0,
                        "strength": 30.0
                    }
                }
            }
        ],
        "spaces": [
            {
                "space_id": "SPACE001",
                "global_id": "5zM0l1N4oP6rS8tU0vW2xY",
                "space_name": "办公室101",
                "space_type": "Room",
                "long_name": "一层办公室101",
                "description": "标准办公室",
                "geometry": {
                    "placement": {
                        "location": {"x": 5.0, "y": 5.0, "z": 0.0}
                    },
                    "representation": {
                        "representation_type": "BRep",
                        "shape": {
                            "volume": 60.0,
                            "area": 20.0
                        }
                    }
                },
                "floor": "F1",
                "elevation": 0.0,
                "height": 3.0
            }
        ],
        "floors": [
            {
                "floor_id": "FLOOR001",
                "global_id": "6aN1m2O5pQ7sT9uV1wX3yZ",
                "floor_name": "一层",
                "elevation": 0.0,
                "height": 3.0
            }
        ]
    }

    # 3. 存储建筑元素
    for element in project_data["building_elements"]:
        element_id = storage.store_building_element(element)
        logger.info(f"Stored building element: {element_id}")

    # 4. 存储空间
    for space in project_data["spaces"]:
        space_id = storage.store_space(space)
        logger.info(f"Stored space: {space_id}")

    # 5. 查询建筑元素
    walls = storage.query_building_elements("Wall")
    logger.info(f"Found {len(walls)} walls")

    # 6. 查询空间
    rooms = storage.query_spaces("Room")
    logger.info(f"Found {len(rooms)} rooms")

    return project_data

# 运行案例1
if __name__ == "__main__":
    case1_building_design_management()
```

**预期结果**：

```text
Stored building element: 1
Stored space: 1
Found 1 walls
Found 1 rooms
```

---

## 3. 案例2：IFC文件解析和存储

### 3.1 场景描述

**业务背景**：
建筑公司需要从IFC文件中提取建筑信息，存储到数据库中，以便后续查询和分析。

**技术挑战**：

- IFC文件格式复杂，需要正确解析
- IFC文件可能很大，需要高效处理
- 需要提取关键信息（建筑元素、空间、材料等）
- 需要处理IFC实体之间的关系

**解决方案**：
使用IFCParser解析IFC文件，提取建筑元素、空间、材料等信息，存储到PostgreSQL数据库中。

### 3.2 Schema定义

**IFC文件解析Schema**：

```json
{
  "ifc_file": {
    "file_path": "/data/building.ifc",
    "file_name": "building.ifc",
    "file_size": 5242880,
    "file_schema": "IFC4",
    "file_author": "Architect A",
    "file_organization": "ABC Architecture",
    "creation_date": "2025-01-21T10:00:00Z"
  },
  "ifc_entities": [
    {
      "entity_id": 1,
      "entity_type": "IFCWALL",
      "global_id": "3xK8j9L2mN4pQ6rS8tU0vW",
      "name": "外墙-东侧",
      "description": "钢筋混凝土外墙",
      "tag": "W-001"
    },
    {
      "entity_id": 2,
      "entity_type": "IFCSPACE",
      "global_id": "5zM0l1N4oP6rS8tU0vW2xY",
      "name": "办公室101",
      "description": "标准办公室"
    }
  ]
}
```

### 3.3 实现代码

**完整的IFC文件解析和存储实现**：

```python
import logging
from typing import Dict
from bim_schema.transformation import IFCParser, BIMStorage

logger = logging.getLogger(__name__)

# 案例2：IFC文件解析和存储
def case2_ifc_file_parsing():
    """案例2：IFC文件解析和存储"""

    # 1. 初始化IFC解析器
    ifc_parser = IFCParser()

    # 2. 解析IFC文件
    ifc_file_path = "/data/building.ifc"
    try:
        ifc_data = ifc_parser.parse_ifc_file(ifc_file_path)
        logger.info(f"Parsed IFC file: {ifc_data['file_path']}")
        logger.info(f"Found {ifc_data['ifc_data']['entity_count']} entities")
    except Exception as e:
        logger.error(f"Failed to parse IFC file: {e}")
        raise

    # 3. 初始化BIM存储
    db_config = {
        "host": "localhost",
        "port": 5432,
        "database": "bim_db",
        "user": "bim_user",
        "password": "bim_password"
    }
    storage = BIMStorage(db_config)
    storage.connect()
    storage.create_tables()

    # 4. 存储IFC文件信息
    file_id = storage.store_ifc_file(ifc_data)
    logger.info(f"Stored IFC file with ID: {file_id}")

    # 5. 解析并存储主要实体
    entity_parser = ifc_parser.IFCEntityParser()
    entities = ifc_data.get("ifc_data", {}).get("entities", [])

    for entity in entities:
        entity_type = entity.get("type")

        if entity_type == "IFCWALL":
            wall_data = entity_parser.parse_ifc_wall(entity)
            if wall_data:
                logger.info(f"Parsed IfcWall: {wall_data.get('name')}")

        elif entity_type == "IFCDOOR":
            door_data = entity_parser.parse_ifc_door(entity)
            if door_data:
                logger.info(f"Parsed IfcDoor: {door_data.get('name')}")

        elif entity_type == "IFCSPACE":
            space_data = entity_parser.parse_ifc_space(entity)
            if space_data:
                logger.info(f"Parsed IfcSpace: {space_data.get('name')}")

    return ifc_data

# 运行案例2
if __name__ == "__main__":
    case2_ifc_file_parsing()
```

**预期结果**：

```text
Parsed IFC file: /data/building.ifc
Found 1250 entities
Stored IFC file with ID: 1
Parsed IfcWall: 外墙-东侧
Parsed IfcDoor: 主入口门
Parsed IfcSpace: 办公室101
```

---

## 4. 案例3：施工管理

### 4.1 场景描述

**业务背景**：
施工公司需要管理施工计划、进度跟踪、质量检查、安全管理等信息，确保施工项目按时按质完成。

**技术挑战**：

- 需要管理复杂的施工任务和依赖关系
- 需要实时跟踪施工进度
- 需要记录质量检查结果
- 需要管理安全风险和事故

**解决方案**：
使用BIM_Schema定义施工管理数据结构，实现施工计划制定、进度跟踪、质量检查、安全管理等功能。

### 4.2 Schema定义

**施工管理Schema**：

```json
{
  "project_id": "PROJ20250121001",
  "project_name": "办公楼A",
  "schedule": {
    "schedule_id": "SCHED001",
    "schedule_name": "办公楼A施工计划",
    "start_date": "2025-02-01",
    "end_date": "2025-12-31",
    "tasks": [
      {
        "task_id": "TASK001",
        "task_name": "基础施工",
        "task_type": "Foundation",
        "planned_start": "2025-02-01",
        "planned_end": "2025-03-15",
        "planned_duration": 43,
        "progress": 75.0,
        "status": "InProgress",
        "assigned_resources": [
          {
            "resource_id": "RES001",
            "resource_type": "Labor",
            "resource_name": "施工队A",
            "quantity": 20.0,
            "unit": "人"
          }
        ],
        "related_elements": ["ELEM001", "ELEM002"]
      }
    ]
  },
  "quality": {
    "inspections": [
      {
        "inspection_id": "INS001",
        "inspection_type": "Structure",
        "inspection_date": "2025-02-20",
        "inspector": "质检员A",
        "inspected_element": "ELEM001",
        "inspection_result": "Pass",
        "inspection_notes": "质量合格"
      }
    ]
  },
  "safety": {
    "hazards": [
      {
        "hazard_id": "HAZ001",
        "hazard_type": "Fall",
        "hazard_location": "二层施工区域",
        "hazard_description": "高空作业风险",
        "risk_level": "High",
        "mitigation_measures": "设置安全网和防护栏",
        "status": "Mitigated"
      }
    ]
  }
}
```

### 4.3 实现代码

**完整的施工管理实现**：

```python
import logging
from typing import Dict
from datetime import date
from bim_schema.transformation import BIMStorage

logger = logging.getLogger(__name__)

# 案例3：施工管理
def case3_construction_management():
    """案例3：施工管理"""

    # 1. 初始化BIM存储
    db_config = {
        "host": "localhost",
        "port": 5432,
        "database": "bim_db",
        "user": "bim_user",
        "password": "bim_password"
    }
    storage = BIMStorage(db_config)
    storage.connect()
    storage.create_tables()

    # 2. 创建施工计划
    construction_data = {
        "project_id": "PROJ20250121001",
        "project_name": "办公楼A",
        "schedule": {
            "schedule_id": "SCHED001",
            "schedule_name": "办公楼A施工计划",
            "start_date": date(2025, 2, 1),
            "end_date": date(2025, 12, 31),
            "tasks": [
                {
                    "task_id": "TASK001",
                    "task_name": "基础施工",
                    "task_type": "Foundation",
                    "planned_start": date(2025, 2, 1),
                    "planned_end": date(2025, 3, 15),
                    "planned_duration": 43,
                    "progress": 75.0,
                    "status": "InProgress",
                    "assigned_resources": [
                        {
                            "resource_id": "RES001",
                            "resource_type": "Labor",
                            "resource_name": "施工队A",
                            "quantity": 20.0,
                            "unit": "人"
                        }
                    ],
                    "related_elements": ["ELEM001", "ELEM002"]
                }
            ]
        },
        "quality": {
            "inspections": [
                {
                    "inspection_id": "INS001",
                    "inspection_type": "Structure",
                    "inspection_date": date(2025, 2, 20),
                    "inspector": "质检员A",
                    "inspected_element": "ELEM001",
                    "inspection_result": "Pass",
                    "inspection_notes": "质量合格"
                }
            ]
        },
        "safety": {
            "hazards": [
                {
                    "hazard_id": "HAZ001",
                    "hazard_type": "Fall",
                    "hazard_location": "二层施工区域",
                    "hazard_description": "高空作业风险",
                    "risk_level": "High",
                    "mitigation_measures": "设置安全网和防护栏",
                    "status": "Mitigated"
                }
            ]
        }
    }

    # 3. 存储施工计划
    schedule_id = storage.store_schedule(construction_data["schedule"])
    logger.info(f"Stored schedule: {schedule_id}")

    # 4. 存储质量检查
    for inspection in construction_data["quality"]["inspections"]:
        inspection_id = storage.store_inspection(inspection)
        logger.info(f"Stored inspection: {inspection_id}")

    # 5. 存储安全风险
    for hazard in construction_data["safety"]["hazards"]:
        hazard_id = storage.store_hazard(hazard)
        logger.info(f"Stored hazard: {hazard_id}")

    # 6. 查询施工进度
    progress = storage.query_progress("PROJ20250121001")
    logger.info(f"Overall progress: {progress['overall_progress']}%")

    return construction_data

# 运行案例3
if __name__ == "__main__":
    case3_construction_management()
```

**预期结果**：

```text
Stored schedule: 1
Stored inspection: 1
Stored hazard: 1
Overall progress: 25.5%
```

---

## 5. 案例4：COBie数据生成

### 5.1 场景描述

**业务背景**：
建筑交付给运营方时，需要生成COBie格式的数据，包含设备清单、维护信息、空间信息等，以便运营方进行设施管理。

**技术挑战**：

- 需要从IFC模型中提取运营相关信息
- 需要生成符合COBie标准的Excel文件
- 需要包含设备、空间、系统、文档等信息
- 需要确保数据的完整性和准确性

**解决方案**：
使用COBieGenerator从IFC数据生成COBie数据，导出为Excel格式，供运营方使用。

### 5.2 Schema定义

**COBie数据生成Schema**：

```json
{
  "version": "2.4",
  "generated_date": "2025-01-21T10:00:00Z",
  "sheets": {
    "Facility": [
      {
        "Name": "办公楼A",
        "CreatedBy": "Architect A",
        "CreatedOn": "2025-01-21T10:00:00Z",
        "Category": "Building",
        "ProjectName": "办公楼A项目",
        "SiteName": "建设路1号",
        "LinearUnits": "Meters",
        "AreaUnits": "SquareMeters",
        "VolumeUnits": "CubicMeters",
        "CurrencyUnit": "CNY"
      }
    ],
    "Space": [
      {
        "Name": "办公室101",
        "CreatedBy": "Architect A",
        "CreatedOn": "2025-01-21T10:00:00Z",
        "Category": "Space",
        "FloorName": "一层",
        "Description": "标准办公室",
        "GrossArea": 20.0,
        "NetArea": 18.0
      }
    ],
    "Component": [
      {
        "Name": "空调机组-001",
        "CreatedBy": "Architect A",
        "CreatedOn": "2025-01-21T10:00:00Z",
        "TypeName": "VRV空调系统",
        "Space": "办公室101",
        "Description": "VRV多联机空调",
        "SerialNumber": "AC-2025-001",
        "InstallationDate": "2025-06-01",
        "TagNumber": "AC-001"
      }
    ]
  }
}
```

### 5.3 实现代码

**完整的COBie数据生成实现**：

```python
import logging
from typing import Dict
from bim_schema.transformation import IFCParser, COBieGenerator

logger = logging.getLogger(__name__)

# 案例4：COBie数据生成
def case4_cobie_generation():
    """案例4：COBie数据生成"""

    # 1. 解析IFC文件
    ifc_parser = IFCParser()
    ifc_file_path = "/data/building.ifc"

    try:
        ifc_data = ifc_parser.parse_ifc_file(ifc_file_path)
        logger.info(f"Parsed IFC file: {ifc_file_path}")
    except Exception as e:
        logger.error(f"Failed to parse IFC file: {e}")
        raise

    # 2. 生成COBie数据
    cobie_generator = COBieGenerator()

    try:
        cobie_data = cobie_generator.generate_cobie_from_ifc(ifc_data)
        logger.info(f"Generated COBie data with {len(cobie_data['sheets'])} sheets")
    except Exception as e:
        logger.error(f"Failed to generate COBie data: {e}")
        raise

    # 3. 导出COBie数据到Excel
    output_dir = "/data/cobie"

    try:
        exported_files = cobie_generator.export_to_csv(cobie_data, output_dir)
        logger.info(f"Exported {len(exported_files)} COBie sheets to {output_dir}")
        for file_path in exported_files:
            logger.info(f"  - {file_path}")
    except Exception as e:
        logger.error(f"Failed to export COBie data: {e}")
        raise

    # 4. 验证COBie数据
    required_sheets = ["Contact", "Facility", "Floor", "Space", "Type", "Component"]
    missing_sheets = [s for s in required_sheets if s not in cobie_data["sheets"]]

    if missing_sheets:
        logger.warning(f"Missing required COBie sheets: {missing_sheets}")
    else:
        logger.info("All required COBie sheets are present")

    return cobie_data

# 运行案例4
if __name__ == "__main__":
    case4_cobie_generation()
```

**预期结果**：

```text
Parsed IFC file: /data/building.ifc
Generated COBie data with 19 sheets
Exported 19 COBie sheets to /data/cobie
  - /data/cobie/Contact.csv
  - /data/cobie/Facility.csv
  - /data/cobie/Floor.csv
  - /data/cobie/Space.csv
  - /data/cobie/Type.csv
  - /data/cobie/Component.csv
All required COBie sheets are present
```

---

## 6. 案例5：gbXML能耗分析

### 6.1 场景描述

**业务背景**：
建筑设计公司需要进行建筑能耗分析，评估建筑的能源性能，优化建筑设计方案。

**技术挑战**：

- 需要从IFC模型生成gbXML文件
- 需要定义建筑的热工参数
- 需要配置HVAC系统和照明系统
- 需要与能耗分析软件（如EnergyPlus）集成

**解决方案**：
使用gbXMLParser解析gbXML文件，或从IFC模型生成gbXML文件，用于能耗分析。

### 6.2 Schema定义

**gbXML能耗分析Schema**：

```json
{
  "version": "6.01",
  "campus": {
    "id": "CAMPUS001",
    "location": {
      "latitude": 31.2304,
      "longitude": 121.4737,
      "elevation": 10.0
    },
    "building": {
      "id": "BUILDING001",
      "building_type": "Office",
      "spaces": [
        {
          "id": "SPACE001",
          "space_type": "Office",
          "volume": 60.0,
          "area": 20.0,
          "people_number": 2.0,
          "lighting_power": 10.0,
          "equipment_power": 5.0
        }
      ],
      "surfaces": [
        {
          "id": "SURFACE001",
          "surface_type": "ExteriorWall",
          "construction_id_ref": "CONSTR001",
          "planar_geometry": {
            "polygon": {
              "points": [
                {"x": 0.0, "y": 0.0, "z": 0.0},
                {"x": 20.0, "y": 0.0, "z": 0.0},
                {"x": 20.0, "y": 0.0, "z": 3.0},
                {"x": 0.0, "y": 0.0, "z": 3.0}
              ]
            }
          }
        }
      ]
    }
  },
  "construction": [
    {
      "id": "CONSTR001",
      "u_value": 0.5,
      "layer_ids": ["LAYER001", "LAYER002"]
    }
  ],
  "material": [
    {
      "id": "MAT001",
      "name": "C30混凝土",
      "r_value": 0.66,
      "thickness": 0.3,
      "conductivity": 1.51,
      "density": 2400.0,
      "specific_heat": 920.0
    }
  ]
}
```

### 6.3 实现代码

**完整的gbXML能耗分析实现**：

```python
import logging
from typing import Dict
from bim_schema.transformation import gbXMLParser

logger = logging.getLogger(__name__)

# 案例5：gbXML能耗分析
def case5_gbxml_energy_analysis():
    """案例5：gbXML能耗分析"""

    # 1. 解析gbXML文件
    gbxml_parser = gbXMLParser()
    gbxml_file_path = "/data/building.xml"

    try:
        gbxml_data = gbxml_parser.parse_gbxml_file(gbxml_file_path)
        logger.info(f"Parsed gbXML file: {gbxml_file_path}")
    except Exception as e:
        logger.error(f"Failed to parse gbXML file: {e}")
        raise

    # 2. 提取建筑信息
    building = gbxml_data.get("campus", {}).get("building", {})
    building_id = building.get("id", "")
    building_type = building.get("building_type", "")
    logger.info(f"Building ID: {building_id}, Type: {building_type}")

    # 3. 提取空间信息
    spaces = building.get("spaces", [])
    logger.info(f"Found {len(spaces)} spaces")

    total_area = sum(space.get("area", 0) for space in spaces)
    total_volume = sum(space.get("volume", 0) for space in spaces)
    logger.info(f"Total area: {total_area} m², Total volume: {total_volume} m³")

    # 4. 提取表面信息
    surfaces = building.get("surfaces", [])
    logger.info(f"Found {len(surfaces)} surfaces")

    exterior_walls = [s for s in surfaces if s.get("surface_type") == "ExteriorWall"]
    logger.info(f"Found {len(exterior_walls)} exterior walls")

    # 5. 提取构造信息
    constructions = gbxml_data.get("construction", [])
    logger.info(f"Found {len(constructions)} constructions")

    for constr in constructions:
        u_value = constr.get("u_value", 0)
        logger.info(f"Construction {constr.get('id')}: U-value = {u_value} W/(m²·K)")

    # 6. 提取材料信息
    materials = gbxml_data.get("material", [])
    logger.info(f"Found {len(materials)} materials")

    for mat in materials:
        mat_name = mat.get("name", "")
        conductivity = mat.get("conductivity", 0)
        logger.info(f"Material {mat_name}: Conductivity = {conductivity} W/(m·K)")

    return gbxml_data

# 运行案例5
if __name__ == "__main__":
    case5_gbxml_energy_analysis()
```

**预期结果**：

```text
Parsed gbXML file: /data/building.xml
Building ID: BUILDING001, Type: Office
Found 50 spaces
Total area: 2000.0 m², Total volume: 6000.0 m³
Found 200 surfaces
Found 80 exterior walls
Found 20 constructions
Construction CONSTR001: U-value = 0.5 W/(m²·K)
Found 30 materials
Material C30混凝土: Conductivity = 1.51 W/(m·K)
```

---

## 7. 案例6：运维管理

### 7.1 场景描述

**业务背景**：
设施管理公司需要管理建筑的设备、维护计划、能耗监测、空间使用等信息，确保建筑正常运营。

**技术挑战**：

- 需要管理大量设备信息
- 需要制定和维护维护计划
- 需要监测和分析能耗数据
- 需要管理空间使用和租赁信息

**解决方案**：
使用BIM_Schema定义运维管理数据结构，实现设备管理、维护计划、能耗监测、空间管理等功能。

### 7.2 Schema定义

**运维管理Schema**：

```json
{
  "facility_id": "FACILITY001",
  "facility_name": "办公楼A",
  "equipment": [
    {
      "equipment_id": "EQ001",
      "equipment_name": "空调机组-001",
      "equipment_type": "HVAC",
      "manufacturer": "大金",
      "model_number": "VRV-S",
      "serial_number": "AC-2025-001",
      "installation_date": "2025-06-01",
      "warranty_start_date": "2025-06-01",
      "warranty_duration": 2,
      "location": {
        "space_id": "SPACE001",
        "space_name": "办公室101",
        "coordinates": {
          "x": 5.0,
          "y": 5.0,
          "z": 2.5
        }
      },
      "status": "Operational"
    }
  ],
  "maintenance": {
    "maintenance_plans": [
      {
        "plan_id": "PLAN001",
        "plan_name": "空调机组定期维护",
        "equipment_id": "EQ001",
        "maintenance_type": "Preventive",
        "frequency": "Monthly",
        "frequency_value": 30,
        "estimated_duration": 2,
        "estimated_cost": 500.0,
        "maintenance_procedures": "1. 清洁过滤器\n2. 检查制冷剂\n3. 检查电气连接"
      }
    ],
    "maintenance_history": [
      {
        "record_id": "REC001",
        "plan_id": "PLAN001",
        "equipment_id": "EQ001",
        "maintenance_date": "2025-01-15",
        "maintenance_type": "Preventive",
        "performed_by": "维护工程师A",
        "duration": 2,
        "cost": 500.0,
        "description": "定期维护完成",
        "next_maintenance_date": "2025-02-15",
        "status": "Completed"
      }
    ]
  },
  "energy": {
    "energy_monitoring": [
      {
        "data_id": "ENERGY001",
        "timestamp": "2025-01-21T10:00:00Z",
        "energy_type": "Electricity",
        "consumption": 1500.0,
        "cost": 1200.0,
        "source": "Main Meter",
        "location": "办公楼A"
      }
    ]
  }
}
```

### 7.3 实现代码

**完整的运维管理实现**：

```python
import logging
from typing import Dict
from datetime import date, datetime
from bim_schema.transformation import BIMStorage

logger = logging.getLogger(__name__)

# 案例6：运维管理
def case6_operation_management():
    """案例6：运维管理"""

    # 1. 初始化BIM存储
    db_config = {
        "host": "localhost",
        "port": 5432,
        "database": "bim_db",
        "user": "bim_user",
        "password": "bim_password"
    }
    storage = BIMStorage(db_config)
    storage.connect()
    storage.create_tables()

    # 2. 创建运维管理数据
    operation_data = {
        "facility_id": "FACILITY001",
        "facility_name": "办公楼A",
        "equipment": [
            {
                "equipment_id": "EQ001",
                "equipment_name": "空调机组-001",
                "equipment_type": "HVAC",
                "manufacturer": "大金",
                "model_number": "VRV-S",
                "serial_number": "AC-2025-001",
                "installation_date": date(2025, 6, 1),
                "warranty_start_date": date(2025, 6, 1),
                "warranty_duration": 2,
                "location": {
                    "space_id": "SPACE001",
                    "space_name": "办公室101",
                    "coordinates": {"x": 5.0, "y": 5.0, "z": 2.5}
                },
                "status": "Operational"
            }
        ],
        "maintenance": {
            "maintenance_plans": [
                {
                    "plan_id": "PLAN001",
                    "plan_name": "空调机组定期维护",
                    "equipment_id": "EQ001",
                    "maintenance_type": "Preventive",
                    "frequency": "Monthly",
                    "frequency_value": 30,
                    "estimated_duration": 2,
                    "estimated_cost": 500.0,
                    "maintenance_procedures": "1. 清洁过滤器\n2. 检查制冷剂\n3. 检查电气连接"
                }
            ],
            "maintenance_history": [
                {
                    "record_id": "REC001",
                    "plan_id": "PLAN001",
                    "equipment_id": "EQ001",
                    "maintenance_date": date(2025, 1, 15),
                    "maintenance_type": "Preventive",
                    "performed_by": "维护工程师A",
                    "duration": 2,
                    "cost": 500.0,
                    "description": "定期维护完成",
                    "next_maintenance_date": date(2025, 2, 15),
                    "status": "Completed"
                }
            ]
        },
        "energy": {
            "energy_monitoring": [
                {
                    "data_id": "ENERGY001",
                    "timestamp": datetime(2025, 1, 21, 10, 0, 0),
                    "energy_type": "Electricity",
                    "consumption": 1500.0,
                    "cost": 1200.0,
                    "source": "Main Meter",
                    "location": "办公楼A"
                }
            ]
        }
    }

    # 3. 存储设备信息
    for equipment in operation_data["equipment"]:
        equipment_id = storage.store_equipment(equipment)
        logger.info(f"Stored equipment: {equipment_id}")

    # 4. 存储维护计划
    for plan in operation_data["maintenance"]["maintenance_plans"]:
        plan_id = storage.store_maintenance_plan(plan)
        logger.info(f"Stored maintenance plan: {plan_id}")

    # 5. 存储维护历史
    for record in operation_data["maintenance"]["maintenance_history"]:
        record_id = storage.store_maintenance_record(record)
        logger.info(f"Stored maintenance record: {record_id}")

    # 6. 存储能耗数据
    for energy_data in operation_data["energy"]["energy_monitoring"]:
        energy_id = storage.store_energy_data(energy_data)
        logger.info(f"Stored energy data: {energy_id}")

    # 7. 查询设备信息
    hvac_equipment = storage.query_equipment("HVAC")
    logger.info(f"Found {len(hvac_equipment)} HVAC equipment")

    # 8. 查询维护计划
    preventive_plans = storage.query_maintenance_plans("Preventive")
    logger.info(f"Found {len(preventive_plans)} preventive maintenance plans")

    return operation_data

# 运行案例6
if __name__ == "__main__":
    case6_operation_management()
```

**预期结果**：

```text
Stored equipment: 1
Stored maintenance plan: 1
Stored maintenance record: 1
Stored energy data: 1
Found 1 HVAC equipment
Found 1 preventive maintenance plans
```

---

## 8. 案例7：BIM数据查询和分析

### 8.1 场景描述

**业务背景**：
建筑公司需要查询和分析BIM数据，生成报表，支持决策制定。

**技术挑战**：

- 需要高效查询大量BIM数据
- 需要支持复杂的查询条件
- 需要生成各种分析报表
- 需要支持数据可视化

**解决方案**：
使用BIMStorage提供的数据查询功能，实现BIM数据的查询和分析。

### 8.2 实现代码

**完整的BIM数据查询和分析实现**：

```python
import logging
from typing import Dict, List
from bim_schema.transformation import BIMStorage

logger = logging.getLogger(__name__)

# 案例7：BIM数据查询和分析
def case7_bim_data_analysis():
    """案例7：BIM数据查询和分析"""

    # 1. 初始化BIM存储
    db_config = {
        "host": "localhost",
        "port": 5432,
        "database": "bim_db",
        "user": "bim_user",
        "password": "bim_password"
    }
    storage = BIMStorage(db_config)
    storage.connect()

    # 2. 查询建筑元素统计
    walls = storage.query_building_elements("Wall")
    doors = storage.query_building_elements("Door")
    windows = storage.query_building_elements("Window")

    logger.info(f"Building elements statistics:")
    logger.info(f"  Walls: {len(walls)}")
    logger.info(f"  Doors: {len(doors)}")
    logger.info(f"  Windows: {len(windows)}")

    # 3. 查询空间统计
    rooms = storage.query_spaces("Room")
    total_area = sum(room.get("area", 0) for room in rooms)
    total_volume = sum(room.get("volume", 0) for room in rooms)

    logger.info(f"Space statistics:")
    logger.info(f"  Rooms: {len(rooms)}")
    logger.info(f"  Total area: {total_area} m²")
    logger.info(f"  Total volume: {total_volume} m³")

    # 4. 查询设备统计
    hvac_equipment = storage.query_equipment("HVAC")
    electrical_equipment = storage.query_equipment("Electrical")

    logger.info(f"Equipment statistics:")
    logger.info(f"  HVAC: {len(hvac_equipment)}")
    logger.info(f"  Electrical: {len(electrical_equipment)}")

    # 5. 查询维护计划统计
    preventive_plans = storage.query_maintenance_plans("Preventive")
    corrective_plans = storage.query_maintenance_plans("Corrective")

    logger.info(f"Maintenance plan statistics:")
    logger.info(f"  Preventive: {len(preventive_plans)}")
    logger.info(f"  Corrective: {len(corrective_plans)}")

    # 6. 生成分析报表
    analysis_report = {
        "building_elements": {
            "walls": len(walls),
            "doors": len(doors),
            "windows": len(windows)
        },
        "spaces": {
            "rooms": len(rooms),
            "total_area": total_area,
            "total_volume": total_volume
        },
        "equipment": {
            "hvac": len(hvac_equipment),
            "electrical": len(electrical_equipment)
        },
        "maintenance": {
            "preventive_plans": len(preventive_plans),
            "corrective_plans": len(corrective_plans)
        }
    }

    logger.info(f"Analysis report: {analysis_report}")

    return analysis_report

# 运行案例7
if __name__ == "__main__":
    case7_bim_data_analysis()
```

**预期结果**：

```text
Building elements statistics:
  Walls: 50
  Doors: 20
  Windows: 80
Space statistics:
  Rooms: 30
  Total area: 2000.0 m²
  Total volume: 6000.0 m³
Equipment statistics:
  HVAC: 10
  Electrical: 15
Maintenance plan statistics:
  Preventive: 8
  Corrective: 2
Analysis report: {...}
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系

---

## 9. 案例8：智能建筑运营系统

### 9.1 场景描述

**业务背景**：
智能建筑运营系统整合BIM数据和IoT传感器数据，
实现建筑设备智能控制、能耗优化、环境舒适度管理。

**技术挑战**：

- 需要BIM数据与IoT数据融合
- 需要设备控制算法
- 需要实时监测
- 需要运营优化

**解决方案**：
使用BIM_Schema整合建筑数据和IoT数据，
使用AI算法进行运营优化，
使用BIMStorage存储运营数据。

### 9.2 Schema定义

**智能建筑运营Schema**：

```dsl
schema SmartBuildingOperations {
  operation_session_id: String @value("BUILDING-OPS-20250121-001") @required
  building_id: String @value("BUILDING-001") @required
  operation_time: DateTime @value("2025-01-21T10:00:00") @required

  building_status: {
    occupancy: Integer @value(500) @unit("people")
    occupancy_rate: Decimal @value(0.75) @range(0.0, 1.0)
    temperature: Decimal @value(22.5) @unit("Celsius")
    humidity: Decimal @value(55.0) @unit("%")
    air_quality: Integer @value(85) @unit("AQI")
    lighting_level: Decimal @value(0.8) @range(0.0, 1.0)
  } @required

  equipment_status: {
    hvac_systems: [
      {
        system_id: String @value("HVAC-001")
        status: Enum { Running } @value(Running)
        power_consumption: Decimal @value(50.5) @unit("kW")
        efficiency: Decimal @value(0.85) @range(0.0, 1.0)
      }
    ]
    lighting_systems: [
      {
        system_id: String @value("LIGHT-001")
        status: Enum { On } @value(On)
        brightness: Integer @value(80) @range(0, 100)
        power_consumption: Decimal @value(5.2) @unit("kW")
      }
    ]
  } @required

  optimization_results: {
    energy_savings: Decimal @value(0.15) @unit("15% reduction")
    comfort_improvement: Decimal @value(0.10) @unit("10% improvement")
    cost_savings: Decimal @value(5000.0) @unit("RMB/month")
  } @required
} @standard("IFC")
```

### 9.3 实现代码

```python
from bim_storage import BIMStorage
from datetime import datetime

def smart_building_operations():
    """智能建筑运营系统示例"""
    storage = BIMStorage("postgresql://user:password@localhost/bim_db")

    # 建筑状态
    building_status = {
        "building_id": "BUILDING-001",
        "occupancy": 500,
        "occupancy_rate": 0.75,
        "temperature": 22.5,
        "humidity": 55.0,
        "air_quality": 85,
        "lighting_level": 0.8
    }

    # 设备状态
    equipment_status = {
        "hvac_systems": [
            {
                "system_id": "HVAC-001",
                "status": "Running",
                "power_consumption": 50.5,
                "efficiency": 0.85
            }
        ],
        "lighting_systems": [
            {
                "system_id": "LIGHT-001",
                "status": "On",
                "brightness": 80,
                "power_consumption": 5.2
            }
        ]
    }

    # 运营优化算法
    def optimize_operations(building_status, equipment_status):
        """优化建筑运营"""
        energy_savings = 0.0
        comfort_improvement = 0.0
        cost_savings = 0.0

        # 根据占用率调整设备
        if building_status["occupancy_rate"] < 0.5:
            # 低占用率时降低能耗
            energy_savings = 0.15
            comfort_improvement = 0.0
        else:
            # 正常占用率时优化舒适度
            energy_savings = 0.10
            comfort_improvement = 0.10

        # 根据环境条件调整
        if building_status["temperature"] > 25.0:
            # 温度过高，优化空调
            energy_savings += 0.05
            comfort_improvement += 0.05

        # 计算成本节约
        total_power = sum(
            h["power_consumption"] for h in equipment_status["hvac_systems"]
        ) + sum(
            l["power_consumption"] for l in equipment_status["lighting_systems"]
        )

        cost_savings = total_power * 24 * 30 * 0.8 * energy_savings  # 假设电价0.8元/kWh

        return {
            "energy_savings": energy_savings,
            "comfort_improvement": comfort_improvement,
            "cost_savings": cost_savings
        }

    # 执行运营优化
    optimization_results = optimize_operations(building_status, equipment_status)

    # 存储运营数据
    operation_data = {
        "operation_session_id": "BUILDING-OPS-20250121-001",
        "building_id": building_status["building_id"],
        "operation_time": datetime.now(),
        "occupancy": building_status["occupancy"],
        "occupancy_rate": building_status["occupancy_rate"],
        "temperature": building_status["temperature"],
        "humidity": building_status["humidity"],
        "air_quality": building_status["air_quality"],
        "lighting_level": building_status["lighting_level"],
        "total_power_consumption": sum(
            h["power_consumption"] for h in equipment_status["hvac_systems"]
        ) + sum(
            l["power_consumption"] for l in equipment_status["lighting_systems"]
        ),
        "energy_savings": optimization_results["energy_savings"],
        "comfort_improvement": optimization_results["comfort_improvement"],
        "cost_savings": optimization_results["cost_savings"]
    }

    # 存储到数据库
    operation_id = storage.store_bim_data(operation_data)
    print(f"Building operations data stored: {operation_id}")

    print(f"\nSmart Building Operations:")
    print(f"  Building: {building_status['building_id']}")
    print(f"  Occupancy: {building_status['occupancy']} ({building_status['occupancy_rate']*100:.1f}%)")
    print(f"  Temperature: {building_status['temperature']:.1f}°C")
    print(f"  Energy savings: {optimization_results['energy_savings']*100:.1f}%")
    print(f"  Comfort improvement: {optimization_results['comfort_improvement']*100:.1f}%")
    print(f"  Cost savings: ¥{optimization_results['cost_savings']:.2f}/month")

    return operation_data

if __name__ == "__main__":
    smart_building_operations()
```

---

## 10. 案例9：建筑能耗优化系统

### 10.1 场景描述

**业务背景**：
建筑能耗优化系统分析建筑能耗数据，
识别能耗热点，优化能耗策略，降低建筑运营成本。

**技术挑战**：

- 需要能耗数据收集
- 需要能耗分析
- 需要优化策略
- 需要效果评估

**解决方案**：
使用BIM_Schema整合能耗数据，
使用优化算法进行能耗优化，
使用BIMStorage存储能耗数据。

### 10.2 Schema定义

**建筑能耗优化Schema**：

```dsl
schema BuildingEnergyOptimization {
  optimization_session_id: String @value("ENERGY-OPT-20250121-001") @required
  building_id: String @value("BUILDING-001") @required
  optimization_period: {
    start_date: Date @value("2025-01-01")
    end_date: Date @value("2025-01-21")
  } @required

  energy_consumption: {
    total_consumption: Decimal @value(50000.0) @unit("kWh")
    hvac_consumption: Decimal @value(30000.0) @unit("kWh")
    lighting_consumption: Decimal @value(10000.0) @unit("kWh")
    equipment_consumption: Decimal @value(10000.0) @unit("kWh")
    consumption_per_area: Decimal @value(50.0) @unit("kWh/m²")
    consumption_per_person: Decimal @value(100.0) @unit("kWh/person")
  } @required

  optimization_analysis: {
    energy_waste_points: [
      {
        location: String @value("3F HVAC System")
        waste_type: String @value("Over-cooling")
        waste_amount: Decimal @value(5000.0) @unit("kWh")
        optimization_potential: Decimal @value(0.15)
      }
    ]
    optimization_strategies: [
      {
        strategy: String @value("优化HVAC运行时间")
        expected_savings: Decimal @value(0.10)
        implementation_cost: Decimal @value(10000.0) @unit("RMB")
        payback_period: Decimal @value(12.0) @unit("months")
      }
    ]
    expected_total_savings: Decimal @value(0.15) @unit("15% reduction")
  } @required
} @standard("gbXML")
```

### 10.3 实现代码

```python
from bim_storage import BIMStorage
from datetime import datetime, date

def building_energy_optimization():
    """建筑能耗优化系统示例"""
    storage = BIMStorage("postgresql://user:password@localhost/bim_db")

    # 能耗数据
    energy_consumption = {
        "building_id": "BUILDING-001",
        "optimization_start_date": date(2025, 1, 1),
        "optimization_end_date": date(2025, 1, 21),
        "total_consumption": 50000.0,
        "hvac_consumption": 30000.0,
        "lighting_consumption": 10000.0,
        "equipment_consumption": 10000.0,
        "building_area": 1000.0,  # m²
        "occupancy": 500
    }

    # 能耗分析算法
    def analyze_energy_consumption(consumption_data):
        """分析能耗"""
        energy_waste_points = []
        optimization_strategies = []

        # 识别能耗浪费点
        hvac_ratio = consumption_data["hvac_consumption"] / consumption_data["total_consumption"]
        if hvac_ratio > 0.6:
            energy_waste_points.append({
                "location": "3F HVAC System",
                "waste_type": "Over-cooling",
                "waste_amount": consumption_data["hvac_consumption"] * 0.15,
                "optimization_potential": 0.15
            })

        # 生成优化策略
        if hvac_ratio > 0.6:
            optimization_strategies.append({
                "strategy": "优化HVAC运行时间",
                "expected_savings": 0.10,
                "implementation_cost": 10000.0,
                "payback_period": 12.0
            })

        # 计算总节约潜力
        expected_total_savings = sum(
            s["expected_savings"] for s in optimization_strategies
        ) / len(optimization_strategies) if optimization_strategies else 0.0

        return {
            "energy_waste_points": energy_waste_points,
            "optimization_strategies": optimization_strategies,
            "expected_total_savings": expected_total_savings
        }

    # 执行能耗分析
    optimization_analysis = analyze_energy_consumption(energy_consumption)

    # 计算单位面积和人均能耗
    consumption_per_area = energy_consumption["total_consumption"] / energy_consumption["building_area"]
    consumption_per_person = energy_consumption["total_consumption"] / energy_consumption["occupancy"]

    # 存储优化数据
    optimization_data = {
        "optimization_session_id": "ENERGY-OPT-20250121-001",
        "building_id": energy_consumption["building_id"],
        "optimization_start_date": energy_consumption["optimization_start_date"],
        "optimization_end_date": energy_consumption["optimization_end_date"],
        "total_consumption": energy_consumption["total_consumption"],
        "hvac_consumption": energy_consumption["hvac_consumption"],
        "lighting_consumption": energy_consumption["lighting_consumption"],
        "equipment_consumption": energy_consumption["equipment_consumption"],
        "consumption_per_area": consumption_per_area,
        "consumption_per_person": consumption_per_person,
        "energy_waste_points": optimization_analysis["energy_waste_points"],
        "optimization_strategies": optimization_analysis["optimization_strategies"],
        "expected_total_savings": optimization_analysis["expected_total_savings"]
    }

    # 存储到数据库
    optimization_id = storage.store_bim_data(optimization_data)
    print(f"Energy optimization data stored: {optimization_id}")

    print(f"\nBuilding Energy Optimization:")
    print(f"  Building: {energy_consumption['building_id']}")
    print(f"  Total consumption: {energy_consumption['total_consumption']:.1f} kWh")
    print(f"  Consumption per area: {consumption_per_area:.1f} kWh/m²")
    print(f"  Consumption per person: {consumption_per_person:.1f} kWh/person")
    print(f"  Energy waste points: {len(optimization_analysis['energy_waste_points'])}")
    print(f"  Optimization strategies: {len(optimization_analysis['optimization_strategies'])}")
    print(f"  Expected total savings: {optimization_analysis['expected_total_savings']*100:.1f}%")

    return optimization_data

if __name__ == "__main__":
    building_energy_optimization()
```

---

## 11. 案例10：建筑维护管理系统

### 11.1 场景描述

**业务背景**：
建筑维护管理系统基于BIM数据制定维护计划，
跟踪维护执行，优化维护策略，延长设备寿命。

**技术挑战**：

- 需要BIM数据与维护数据关联
- 需要维护计划制定
- 需要维护执行跟踪
- 需要维护效果评估

**解决方案**：
使用BIM_Schema整合维护数据，
使用维护算法制定维护计划，
使用BIMStorage存储维护数据。

### 11.2 Schema定义

**建筑维护管理Schema**：

```dsl
schema BuildingMaintenanceManagement {
  maintenance_session_id: String @value("MAINT-20250121-001") @required
  building_id: String @value("BUILDING-001") @required
  equipment_id: String @value("EQUIP-001") @required

  equipment_info: {
    equipment_type: String @value("HVAC System")
    manufacturer: String @value("Manufacturer A")
    installation_date: Date @value("2020-01-15")
    warranty_expiry: Date @value("2025-01-15")
    last_maintenance_date: Date @value("2024-12-15")
    maintenance_interval: Integer @value(30) @unit("days")
  } @required

  maintenance_plan: {
    maintenance_type: Enum { Preventive } @value(Preventive)
    scheduled_date: Date @value("2025-01-25")
    maintenance_tasks: [
      {
        task: String @value("更换过滤器")
        priority: Enum { High } @value(High)
        estimated_duration: Integer @value(2) @unit("hours")
        required_parts: [String] @value(["Filter-001"])
      },
      {
        task: String @value("清洁设备")
        priority: Enum { Medium } @value(Medium)
        estimated_duration: Integer @value(1) @unit("hours")
      }
    ]
    estimated_cost: Decimal @value(500.0) @unit("RMB")
  } @required

  maintenance_history: {
    total_maintenances: Integer @value(24)
    average_interval: Decimal @value(30.5) @unit("days")
    total_cost: Decimal @value(12000.0) @unit("RMB")
    equipment_reliability: Decimal @value(0.95) @range(0.0, 1.0)
  } @required
} @standard("COBie")
```

### 11.3 实现代码

```python
from bim_storage import BIMStorage
from datetime import datetime, date, timedelta

def building_maintenance_management():
    """建筑维护管理系统示例"""
    storage = BIMStorage("postgresql://user:password@localhost/bim_db")

    # 设备信息
    equipment_info = {
        "equipment_id": "EQUIP-001",
        "building_id": "BUILDING-001",
        "equipment_type": "HVAC System",
        "manufacturer": "Manufacturer A",
        "installation_date": date(2020, 1, 15),
        "warranty_expiry": date(2025, 1, 15),
        "last_maintenance_date": date(2024, 12, 15),
        "maintenance_interval": 30  # days
    }

    # 维护计划制定算法
    def create_maintenance_plan(equipment_info):
        """制定维护计划"""
        days_since_last_maintenance = (date.today() - equipment_info["last_maintenance_date"]).days

        # 检查是否需要维护
        if days_since_last_maintenance >= equipment_info["maintenance_interval"]:
            scheduled_date = date.today() + timedelta(days=5)

            maintenance_tasks = [
                {
                    "task": "更换过滤器",
                    "priority": "High",
                    "estimated_duration": 2,
                    "required_parts": ["Filter-001"]
                },
                {
                    "task": "清洁设备",
                    "priority": "Medium",
                    "estimated_duration": 1,
                    "required_parts": []
                }
            ]

            estimated_cost = sum(
                200 if task["priority"] == "High" else 100
                for task in maintenance_tasks
            )

            return {
                "maintenance_type": "Preventive",
                "scheduled_date": scheduled_date,
                "maintenance_tasks": maintenance_tasks,
                "estimated_cost": estimated_cost
            }

        return None

    # 制定维护计划
    maintenance_plan = create_maintenance_plan(equipment_info)

    # 维护历史数据
    maintenance_history = {
        "total_maintenances": 24,
        "average_interval": 30.5,
        "total_cost": 12000.0,
        "equipment_reliability": 0.95
    }

    # 存储维护数据
    if maintenance_plan:
        maintenance_data = {
            "maintenance_session_id": "MAINT-20250121-001",
            "building_id": equipment_info["building_id"],
            "equipment_id": equipment_info["equipment_id"],
            "equipment_type": equipment_info["equipment_type"],
            "manufacturer": equipment_info["manufacturer"],
            "installation_date": equipment_info["installation_date"],
            "warranty_expiry": equipment_info["warranty_expiry"],
            "last_maintenance_date": equipment_info["last_maintenance_date"],
            "maintenance_interval": equipment_info["maintenance_interval"],
            "maintenance_type": maintenance_plan["maintenance_type"],
            "scheduled_date": maintenance_plan["scheduled_date"],
            "maintenance_tasks": maintenance_plan["maintenance_tasks"],
            "estimated_cost": maintenance_plan["estimated_cost"],
            "total_maintenances": maintenance_history["total_maintenances"],
            "average_interval": maintenance_history["average_interval"],
            "total_cost": maintenance_history["total_cost"],
            "equipment_reliability": maintenance_history["equipment_reliability"]
        }

        # 存储到数据库
        maintenance_id = storage.store_bim_data(maintenance_data)
        print(f"Maintenance plan stored: {maintenance_id}")

        print(f"\nBuilding Maintenance Management:")
        print(f"  Equipment: {equipment_info['equipment_id']}")
        print(f"  Equipment type: {equipment_info['equipment_type']}")
        print(f"  Scheduled date: {maintenance_plan['scheduled_date']}")
        print(f"  Maintenance tasks: {len(maintenance_plan['maintenance_tasks'])}")
        print(f"  Estimated cost: ¥{maintenance_plan['estimated_cost']:.2f}")
        print(f"  Equipment reliability: {maintenance_history['equipment_reliability']:.2f}")

        return maintenance_data
    else:
        print("No maintenance required at this time")
        return None

if __name__ == "__main__":
    building_maintenance_management()
```

---

**创建时间**：2025-01-21
**最后更新**：2025-01-21
